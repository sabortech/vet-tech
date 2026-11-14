"""Fluxos reais dos assets com ponte simulada, sem chamadas ao Xano/n8n."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'openspec/changes/reorganizar-fluxos-chat/evidence'
MOCK = """() => {
 window.__vetTechChatReady=true;
 window.probe={requests:[],fail:false};
 document.addEventListener('submit',e=>{
  if(e.target.id!=='vettech-chat-bridge')return;
  e.preventDefault();
  const d=JSON.parse(document.getElementById('vettech-chat-payload').value);
  probe.requests.push(d);
  const detail={request_id:d.request_id,conversation_id:d.conversation_id,ok:true};
  if(d.action==='message')Object.assign(detail,{reply:'Vamos encaminhar seu pet.',handoff:true});
  else if(d.action==='support_pets')detail.pets=[{id:1,name:'Luna'}];
  else if(d.action==='support_list')detail.tickets=[{id:19,status:'encerrado',own:true,created_at:1700000000000}];
  else if(d.action.startsWith('support_')) {
   if(probe.fail)Object.assign(detail,{ok:false,error:'Não foi possível concluir o atendimento.'});
   else detail.ticket={id:21,pet:{name:'Luna'},status:d.action==='support_close'?'encerrado':'aguardando',context:[],messages:[],events:[]};
  }else return;
  queueMicrotask(()=>window.dispatchEvent(new CustomEvent(d.action==='message'?'vettech:chat-response':'vettech:support-response',{detail})));
 });
}"""


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=args.chromium)
  for width,theme in [(390,'dark'),(1366,'light'),(320,'light'),(390,'light')]:
   page=browser.new_page(viewport={'width':width,'height':900})
   page.on('pageerror',lambda error: print('Browser error:',error))
   page.route('https://chat.test/**',lambda route: route.fulfill(body=(ROOT/'assets'/route.request.url.split('chat.test/')[1]).read_bytes()) if (ROOT/'assets'/route.request.url.split('chat.test/')[1]).is_file() else route.fulfill(body=''))
   page.goto('https://chat.test/')
   page.set_content('<html><body><div id="vettech-chat-session" data-chat-key="tutor:7" data-chat-name="Ana"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form><button id="vettech-mascote">Abrir</button></body></html>')
   page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'))
   page.add_style_tag(path=str(ROOT/'assets/support-chat.css'))
   if theme=='dark':page.evaluate("document.documentElement.classList.add('dark');document.documentElement.setAttribute('data-vt-theme','dark')")
   page.evaluate('('+MOCK+')()')
   page.clock.install()
   page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   chat=page.locator('#vettech-support-chat')
   expect(chat).to_be_visible()
   page.screenshot(path=str(OUT/f'assistant-{width}-{theme}.png'))
   page.get_by_role('textbox',name='Digite sua pergunta').fill('Falar com veterinário')
   page.get_by_role('button',name='Enviar mensagem').click()
   expect(page.get_by_role('combobox',name='Pet do atendimento')).to_be_visible()
   assert page.evaluate("probe.requests.filter(r=>r.action==='support_list').length")==0
   expect(chat).not_to_contain_text('Atendimento #19')
   page.get_by_role('combobox').select_option('1')
   page.get_by_role('checkbox').check()
   page.screenshot(path=str(OUT/f'handoff-{width}-{theme}.png'))
   page.evaluate('probe.fail=true')
   page.get_by_role('button',name='Confirmar encaminhamento').click()
   expect(page.get_by_role('button',name='Tentar atendimento novamente')).to_be_visible()
   page.screenshot(path=str(OUT/f'error-{width}-{theme}.png'))
   page.evaluate('probe.fail=false')
   page.get_by_role('button',name='Tentar atendimento novamente').click()
   info=page.get_by_role('button',name='Informações do atendimento: Aguardando veterinário',exact=True)
   expect(info).to_be_visible()
   before=page.evaluate('probe.requests.length')
   info.click()
   details=page.get_by_role('dialog',name='Informações do atendimento',exact=True)
   expect(details).to_contain_text('Seu chamado foi enviado')
   assert page.evaluate('probe.requests.length')==before
   page.get_by_role('textbox',name='Motivo do encerramento').fill('Rascunho')
   page.keyboard.press('Escape')
   expect(details).not_to_be_visible()
   expect(info).to_be_focused()
   expect(chat).to_be_visible()
   info.click()
   expect(page.get_by_role('textbox',name='Motivo do encerramento')).to_have_value('Rascunho')
   page.get_by_role('button',name='Fechar informações do atendimento').click()
   creates=page.evaluate("probe.requests.filter(r=>r.action==='support_create')")
   assert len(creates)==2 and creates[0]['operation_id']==creates[1]['operation_id']
   assert creates[0]['pet_id']==creates[1]['pet_id']==1
   count=page.evaluate('probe.requests.length')
   page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true})")
   page.clock.fast_forward(60000)
   assert page.evaluate('probe.requests.length')==count
   page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false})")
   page.clock.fast_forward(21000)
   assert page.evaluate("probe.requests.filter(r=>r.action==='support_get').length")==1
   info.click()
   page.screenshot(path=str(OUT/f'ticket-info-{width}-{theme}.png'))
   page.get_by_role('textbox',name='Motivo do encerramento').fill('Obrigado')
   page.get_by_role('button',name='Cancelar chamado').click()
   expect(details).to_contain_text('Este atendimento foi encerrado')
   page.get_by_role('button',name='Fechar informações do atendimento').click()
   count=page.evaluate('probe.requests.length')
   page.clock.fast_forward(60000)
   assert page.evaluate('probe.requests.length')==count
   page.screenshot(path=str(OUT/f'closed-{width}-{theme}.png'))
   page.get_by_role('button',name='Atendimentos',exact=True).click()
   expect(chat).to_contain_text('Atendimento #19')
   page.screenshot(path=str(OUT/f'list-{width}-{theme}.png'))
   count=page.evaluate('probe.requests.length')
   page.clock.fast_forward(60000)
   assert page.evaluate('probe.requests.length')==count
   page.get_by_role('button',name='Nova conversa',exact=True).click()
   expect(chat).not_to_contain_text('Atendimento #19')
   expect(chat).to_contain_text('Olá, Ana!')
   page.get_by_role('button',name='Fechar chat',exact=True).click()
   page.clock.fast_forward(300)
   page.wait_for_function("probe.requests.at(-1)?.action==='close'")
   count=page.evaluate('probe.requests.length')
   page.clock.fast_forward(60000)
   assert page.evaluate('probe.requests.length')==count
   assert page.evaluate("document.querySelector('dialog').scrollWidth<=document.querySelector('dialog').clientWidth")
   page.close()
  browser.close()
 print('OK: encaminhamento, retry idempotente, isolamento, polling e screenshots em 4 combinações.')


if __name__=='__main__':main()
