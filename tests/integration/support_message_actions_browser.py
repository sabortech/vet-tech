"""Select/edit/delete own human messages with simulated transport only."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
MOCK=r"""() => {
 window.__vetTechChatReady=true;
 const profile=document.getElementById('vettech-chat-session').dataset.chatKey.split(':')[0];
 const peer=profile==='tutor'?'veterinario':'tutor';
 window.actionProbe={requests:[],status:'em_atendimento',failNext:false,messages:[
 {id:'11111111-1111-4111-8111-111111111111',author_profile:peer,author_id:9,text:'Mensagem do interlocutor',at:Date.now()-1000},
 {id:'22222222-2222-4222-8222-222222222222',author_profile:profile,author_id:7,text:'Original',revision:0,read_at:1700000000100,at:Date.now()-500}]};
 document.addEventListener('submit',event=>{
  if(event.target.id!=='vettech-chat-bridge')return;event.preventDefault();
  const d=JSON.parse(document.getElementById('vettech-chat-payload').value);actionProbe.requests.push(d);
  if(!d.action.startsWith('support_'))return;
  const result={request_id:d.request_id,conversation_id:d.conversation_id,ok:true};
  if(d.action==='support_list')result.tickets=[{id:1,own:true,status:actionProbe.status,tutor:{name:'Ana'}}];
  else {
   if(['support_edit','support_delete'].includes(d.action)){
    const row=actionProbe.messages.find(m=>m.id===d.message_id);
    if(actionProbe.failNext){actionProbe.failNext=false;Object.assign(result,{ok:false,error:'Falha temporária de teste.'});}
    else if(d.expected_revision!==(row.revision||0)){Object.assign(result,{ok:false,retryable:false,error:'A mensagem foi alterada. Atualize a conversa antes de tentar novamente.'});}
    else if(d.action==='support_edit')Object.assign(row,{text:d.message,edited_at:1700000000200,revision:row.revision+1,read_at:null});
    else Object.assign(row,{text:'',deleted_at:1700000000300,revision:row.revision+1});
   }
   if(d.read_through){const r=actionProbe.messages.find(m=>m.id===d.read_through);if(r&&!r.deleted_at&&(r.revision||0)===(d.read_revision||0))r.read_at=1700000000400;}
   if(result.ok)result.ticket={id:1,pet:{name:'Luna'},tutor:{name:'Ana'},veterinarian:{name:'Marina',crmv:'123',uf:'SP'},status:actionProbe.status,events:[],context:[],messages:JSON.parse(JSON.stringify(actionProbe.messages))};
  }
  queueMicrotask(()=>window.dispatchEvent(new CustomEvent('vettech:support-response',{detail:result})));
 });
}"""


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args()
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=args.chromium)
  for profile,theme in [('tutor','dark'),('veterinario','light')]:
   page=browser.new_page(viewport={'width':390,'height':844})
   page.route('https://chat.test/**',lambda route:route.fulfill(body=''))
   page.goto('https://chat.test/')
   page.set_content(f'<div id="vettech-chat-session" data-chat-key="{profile}:7"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form><button id="vettech-mascote">Abrir</button>')
   page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'));page.add_style_tag(path=str(ROOT/'assets/support-chat.css'))
   page.evaluate('theme=>document.documentElement.dataset.vtTheme=theme',theme)
   page.evaluate('('+MOCK+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   page.get_by_role('button',name='Atendimentos',exact=True).click();page.get_by_role('button',name='Ver conversa',exact=True).click()
   expect(page.locator('.vt-chat-start-time')).to_have_count(1)
   expect(page.locator('.vt-chat-start-time')).to_have_text(__import__('re').compile(r'\d{2}:\d{2}'))
   expect(page.locator('.vt-chat-row:not(.is-user) .vt-chat-message-menu-trigger')).to_have_count(0)
   expect(page.locator('.vt-chat-message-menu-trigger')).to_have_count(1)
   own=page.locator('.vt-chat-row.is-user .vt-chat-bubble')
   modal=page.get_by_role('dialog',name='Opções da mensagem',exact=True)
   own.get_by_role('button',name='Opções da mensagem',exact=True).click()
   modal.get_by_role('button',name='Editar mensagem',exact=True).click()
   expect(modal.get_by_role('textbox',name='Editar mensagem')).to_have_value('Original')
   modal.get_by_role('button',name='Cancelar',exact=True).click()
   own.click();expect(modal).to_be_visible()
   modal.get_by_role('button',name='Editar mensagem',exact=True).click()
   editor=page.get_by_role('textbox',name='Editar mensagem',exact=True);expect(editor).to_have_value('Original')
   editor.fill('Atualizada <b> 🐾');page.evaluate('actionProbe.failNext=true')
   page.get_by_role('button',name='Salvar alteração',exact=True).click();expect(modal).to_contain_text('Falha temporária de teste.')
   expect(editor).to_have_value('Atualizada <b> 🐾')
   page.get_by_role('button',name='Tentar atendimento novamente',exact=True).click();expect(modal).not_to_be_visible()
   edits=page.evaluate("actionProbe.requests.filter(r=>r.action==='support_edit')")
   assert len(edits)==2 and edits[0]['operation_id']==edits[1]['operation_id']
   expect(own.locator('p')).to_have_text('Atualizada <b> 🐾');expect(own.locator('b')).to_have_count(0)
   expect(own.locator('.vt-chat-edited')).to_have_text(' · Editada');expect(own.locator('.vt-chat-receipt')).to_have_text('Entregue')
   page.screenshot(path=str(ROOT/f'openspec/changes/reorganizar-fluxos-chat/evidence/message-edited-{profile}-{theme}.png'))
   own.focus();page.keyboard.press('Enter');expect(modal).to_be_visible()
   modal.get_by_role('button',name='Apagar mensagem',exact=True).click();modal.get_by_role('button',name='Cancelar',exact=True).click()
   assert not page.evaluate("actionProbe.requests.some(r=>r.action==='support_delete')")
   own.get_by_role('button',name='Opções da mensagem',exact=True).click()
   expect(modal.get_by_role('button',name='Editar mensagem').locator('svg')).to_have_count(1)
   expect(modal.get_by_role('button',name='Apagar mensagem').locator('svg')).to_have_count(1)
   modal.get_by_role('button',name='Apagar mensagem',exact=True).click()
   page.screenshot(path=str(ROOT/f'openspec/changes/reorganizar-fluxos-chat/evidence/message-delete-{profile}-{theme}.png'))
   page.get_by_role('button',name='Confirmar exclusão',exact=True).click();expect(modal).not_to_be_visible()
   expect(page.locator('.vt-chat-row.is-user p')).to_have_text('Mensagem apagada')
   assert page.locator('.vt-chat-row.is-user p').evaluate("el=>el.firstChild.nodeType===Node.TEXT_NODE&&el.lastElementChild.classList.contains('vt-chat-icon')")
   expect(page.locator('.vt-chat-start-time')).to_have_count(1)
   expect(page.locator('.vt-chat-message-menu-trigger')).to_have_count(0)
   page.close()
  browser.close()
 print('OK: own-only selection, keyboard menu, edit/retry, safe text, edited label, delete confirmation and tombstone in both profiles.')


if __name__=='__main__':main()
