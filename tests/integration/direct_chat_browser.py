"""Direct messaging UI against deterministic, private simulated transport."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
MOCK=r'''() => {
window.__vetTechChatReady=true;window.requests=[];window.rows=[];
document.addEventListener('submit',e=>{
 if(e.target.id!=='vettech-chat-bridge')return;e.preventDefault();
 const d=JSON.parse(document.getElementById('vettech-chat-payload').value);requests.push(d);
 if(!d.action.startsWith('direct_'))return;
 const r={request_id:d.request_id,conversation_id:d.conversation_id,ok:true,server_time:Date.now()};
 if(d.action==='direct_tutors')r.tutors=[{id:9,name:'Ana Teste'}];
 else if(d.action==='direct_veterinarians')r.veterinarians=[{id:9,name:'Marina Teste'}];
 else if(d.action==='direct_list')r.threads=[{id:3,peer:{name:'Interlocutor Teste'},unread:1}];
 else {
  if(d.action==='direct_send')rows.push({id:d.operation_id,author_profile:document.getElementById('vettech-chat-session').dataset.chatKey.split(':')[0],author_id:7,text:d.message,at:Date.now()});
  if(d.action==='direct_edit'){const m=rows.find(m=>m.id===d.message_id);m.text=d.message;m.revision=(m.revision||0)+1;m.edited_at=Date.now();}
  if(d.action==='direct_delete'){const m=rows.find(m=>m.id===d.message_id);m.text='';m.deleted_at=Date.now();m.revision=(m.revision||0)+1;}
  r.thread={id:3,tutor:{name:'Ana Teste'},veterinarian:{name:'Marina Teste'},messages:rows};
 }
 queueMicrotask(()=>window.dispatchEvent(new CustomEvent('vettech:direct-response',{detail:r})));
});
}'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--chromium');a=ap.parse_args()
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=a.chromium)
  for profile in ('veterinario','tutor'):
   page=browser.new_page(viewport={'width':430,'height':930});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.route('https://chat.test/**',lambda route:route.fulfill(body=''));page.route('**/optimized/espreitando.webp',lambda route:route.fulfill(path=str(ROOT/'assets/optimized/espreitando.webp'),content_type='image/webp'));page.goto('https://chat.test/')
   page.set_content(f'<div id="vettech-chat-session" data-chat-key="{profile}:7"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form>')
   page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'));page.add_style_tag(path=str(ROOT/'assets/support-chat.css'));page.evaluate('('+MOCK+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   label='Falar com tutor' if profile=='veterinario' else 'Falar com veterinário'
   page.get_by_role('button',name=label,exact=True).click();picker=page.get_by_role('dialog',name=label,exact=True)
   expect(picker).to_be_visible();expect(picker.locator(':scope > .vt-chat-status-led')).to_have_count(1)
   expect(picker.locator('.vt-chat-direct-mascot')).to_be_visible();page.wait_for_function("document.querySelector('.vt-chat-direct-mascot').naturalWidth>0")
   expect(picker.locator('.vt-chat-direct-card > .vt-chat-status-led')).to_have_count(1)
   evidence=ROOT/'openspec/changes/conversas-diretas-veterinario-tutor/evidence';evidence.mkdir(exist_ok=True)
   page.screenshot(path=str(evidence/f'seletor-{profile}.png'))
   picker.get_by_role('textbox',name='Buscar tutor' if profile=='veterinario' else 'Buscar veterinário').fill('Teste')
   before=page.evaluate('requests.length');page.wait_for_timeout(100);assert page.evaluate('requests.length')==before
   picker.get_by_role('button',name='Buscar',exact=True).click();picker.get_by_role('button',name='Conversar',exact=True).click();expect(picker).not_to_be_visible()
   expect(page.locator('.vt-chat-header h2')).to_have_text('Ana Teste' if profile=='veterinario' else 'Marina Teste')
   expect(page.locator('.vt-chat-floating-info')).not_to_be_visible()
   field=page.get_by_placeholder('Digite sua mensagem…');field.fill('Olá direto 🐾');field.press('Enter')
   expect(page.locator('.vt-chat-bubble')).to_contain_text('Olá direto 🐾')
   assert page.evaluate("requests.some(d=>d.action==='direct_send'&&d.thread_id===3)")
   assert not page.evaluate("requests.some(d=>d.action.startsWith('support_'))")
   expect(page.get_by_role('button',name='Opções da mensagem',exact=True)).to_be_visible()
   page.get_by_role('button',name='Opções da mensagem',exact=True).click()
   page.get_by_role('button',name='Editar mensagem',exact=True).click()
   page.get_by_role('textbox',name='Editar mensagem',exact=True).fill('Editada direta')
   page.get_by_role('button',name='Salvar alteração',exact=True).click()
   expect(page.locator('.vt-chat-bubble')).to_contain_text('Editada direta')
   page.get_by_role('button',name='Opções da mensagem',exact=True).click()
   page.get_by_role('button',name='Apagar mensagem',exact=True).click()
   page.get_by_role('button',name='Confirmar exclusão',exact=True).click()
   expect(page.locator('.vt-chat-bubble')).to_contain_text('Mensagem apagada')
   assert page.evaluate("requests.some(d=>d.action==='direct_delete'&&d.thread_id===3)")
   assert not errors,errors
   evidence=ROOT/'openspec/changes/conversas-diretas-veterinario-tutor/evidence';evidence.mkdir(exist_ok=True)
   page.screenshot(path=str(evidence/f'{profile}-conversa.png'))
   page.close()
  browser.close()
 print('direct_chat_browser: veterinarian directory, tutor inbox, private routing and shared composer passed')
if __name__=='__main__':main()
