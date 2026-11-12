"""Confirmação, falha/retry e avisos na UI; ponte simulada, sem chamadas n8n/Xano."""
import argparse
from playwright.sync_api import sync_playwright, expect

MOCK=r'''() => {
  window.supportUIProbe={requests:[],sends:0,ticket:null};
  document.addEventListener('submit',e=>{
    if(e.target.id!=='vettech-chat-bridge')return;
    e.preventDefault();e.stopImmediatePropagation();
    const d=JSON.parse(document.getElementById('vettech-chat-payload').value);
    supportUIProbe.requests.push(d);
    if(d.action==='message'){
      setTimeout(()=>window.dispatchEvent(new CustomEvent('vettech:chat-response',{detail:{request_id:d.request_id,conversation_id:d.conversation_id,ok:true,reply:'Podemos encaminhar a dúvida.',handoff:true,error:null}})),20);
      return;
    }
    if(!d.action.startsWith('support_'))return;
    const action=d.action.slice(8),p=supportUIProbe;
    let result={};
    if(action==='list')result={pets:[{id:1,name:'Pet sintético'}],tickets:p.ticket?[{id:42,status:p.ticket.status,own:true,events:p.ticket.events}]:[]};
    if(action==='create')p.ticket={id:42,status:'aguardando',pet:{id:1,name:'Pet sintético'},context:[],messages:[],events:[],veterinarian:null};
    if(action==='get'&&p.ticket.status==='aguardando'){
      p.ticket.status='em_atendimento';p.ticket.veterinarian={name:'Veterinária sintética',crmv:'QA123',uf:'SP'};
      p.ticket.events=[{id:1,action:'claim',actor_profile:'veterinario',at:Date.now()}];
    }
    if(action==='send'){
      p.sends++;
      if(p.sends===1)result={ok:false,error:'Falha simulada de confirmação.'};
      else if(!p.ticket.messages.some(m=>m.id===d.operation_id))p.ticket.messages.push({id:d.operation_id,author_profile:'tutor',text:d.message,at:Date.now()});
    }
    if(action==='close'){
      p.ticket.status='encerrado';p.ticket.events.push({id:2,action:'close',actor_profile:'veterinario',reason:d.reason,at:Date.now()});
    }
    if(action!=='list'&&result.ok!==false)result={ticket:structuredClone(p.ticket)};
    const detail={request_id:d.request_id,conversation_id:d.conversation_id,action,ok:true,...result};
    setTimeout(()=>window.dispatchEvent(new CustomEvent('vettech:support-response',{detail})),20);
  },true);
}'''

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:3002')
parser.add_argument('--chromium',default='C:/Program Files/Google/Chrome/Application/chrome.exe')
args=parser.parse_args()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path=args.chromium)
    page=b.new_page();page.add_init_script('('+MOCK+')();')
    page.goto(args.url.rstrip('/')+'/login')
    page.wait_for_function('window.__vetTechChatReady === true')
    page.evaluate("() => {const e=document.getElementById('vettech-chat-session');e.dataset.chatKey='tutor:fixture';e.dataset.chatName='Tutora sintética';}")
    page.locator('#vettech-mascote').click()
    page.get_by_role('dialog',name='Assistente Vet Tech').evaluate('el=>Promise.all(el.getAnimations().map(a=>a.finished))')
    page.get_by_role('textbox',name='Digite sua pergunta').fill('Preciso de orientação para meu pet')
    page.get_by_role('button',name='Enviar mensagem',exact=True).click()
    expect(page.get_by_role('combobox',name='Pet do atendimento')).to_be_visible()
    page.get_by_role('button',name='Confirmar encaminhamento',exact=True).click()
    assert page.evaluate("supportUIProbe.requests.filter(r=>r.action==='support_create').length") == 0
    page.get_by_role('button',name='Continuar com o assistente',exact=True).click()
    expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_enabled()
    page.get_by_role('textbox',name='Digite sua pergunta').fill('Pode propor o encaminhamento novamente')
    page.get_by_role('button',name='Enviar mensagem',exact=True).click()
    expect(page.get_by_role('combobox',name='Pet do atendimento')).to_be_visible()
    page.get_by_role('combobox',name='Pet do atendimento').select_option('1')
    page.get_by_role('checkbox').check()
    page.get_by_role('button',name='Confirmar encaminhamento',exact=True).click()
    expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_disabled()
    created=page.evaluate("supportUIProbe.requests.find(r=>r.action==='support_create')")
    assert created['pet_id']==1 and created['consent'] is True
    assert 'context' not in created and 'bridge_key' not in created
    page.get_by_role('button',name='Meus atendimentos / fila',exact=True).click()
    page.get_by_role('button',name='#42 · aguardando · Meu atendimento',exact=True).click()
    expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_enabled()
    page.get_by_role('textbox',name='Digite sua pergunta').fill('Mensagem com retry')
    page.get_by_role('button',name='Enviar mensagem',exact=True).click()
    page.get_by_role('button',name='Tentar atendimento novamente',exact=True).click()
    expect(page.get_by_text('Tutor: Mensagem com retry',exact=True)).to_be_visible()
    sent=page.evaluate("supportUIProbe.requests.filter(r=>r.action==='support_send')")
    assert len(sent)==2 and sent[0]['operation_id']==sent[1]['operation_id']
    assert page.get_by_text('Tutor: Mensagem com retry',exact=True).count()==1
    page.get_by_role('textbox',name='Motivo do encerramento').fill('Orientação concluída')
    page.get_by_role('button',name='Encerrar atendimento',exact=True).click()
    expect(page.get_by_text('Atendimento encerrado: Orientação concluída',exact=True)).to_be_visible()
    expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_disabled()
    page.evaluate("supportUIProbe.ticket.events.push({id:99,action:'send',actor_profile:'veterinario',at:Date.now()});supportUIProbe.ticket.messages.push({id:'notice-fixture',author_profile:'veterinario',text:'Nova orientação sintética',at:Date.now()})")
    page.get_by_role('button',name='Meus atendimentos / fila',exact=True).click()
    notice=page.get_by_text('Atendimento #42: Nova mensagem',exact=True)
    expect(notice).to_be_visible()
    page.get_by_role('button',name='Atualizar atendimentos',exact=True).click()
    expect(page.get_by_role('button',name='#42 · encerrado · Meu atendimento',exact=True)).to_be_visible()
    assert notice.count()==1
    page.get_by_role('button',name='#42 · encerrado · Meu atendimento',exact=True).click()
    expect(page.get_by_text('Veterinário: Nova orientação sintética',exact=True)).to_be_visible()
    page.get_by_role('button',name='Meus atendimentos / fila',exact=True).click()
    expect(page.get_by_role('button',name='#42 · encerrado · Meu atendimento',exact=True)).to_be_visible()
    expect(notice).not_to_be_visible()
    page.get_by_role('button',name='Voltar ao assistente',exact=True).click()
    expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_enabled()
    b.close()
    print('PASS: confirmação exige pet/consentimento, contexto não vem do navegador, retry preserva operação, encerrado somente leitura e retorno ao bot.')
