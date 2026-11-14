"""Delivered/read presentation and visibility guards with a simulated bridge."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
MOCK=r"""() => {
 window.__vetTechChatReady=true;window.probe={requests:[],peerRead:false,receivedRead:false};
 const incoming='11111111-1111-4111-8111-111111111111',outgoing='22222222-2222-4222-8222-222222222222';
 document.addEventListener('submit',event=>{
  if(event.target.id!=='vettech-chat-bridge')return;event.preventDefault();
  const d=JSON.parse(document.getElementById('vettech-chat-payload').value);probe.requests.push(d);
  if(!d.action.startsWith('support_'))return;
  const viewer=document.getElementById('vettech-chat-session').dataset.chatKey.split(':')[0];const peer=viewer==='tutor'?'veterinario':'tutor';
  if(d.read_through===incoming)probe.receivedRead=true;
  const detail={request_id:d.request_id,conversation_id:d.conversation_id,ok:true};
  if(d.action==='support_list')detail.tickets=[{id:1,status:'em_atendimento',own:true,tutor:{name:'Ana'}}];
  else detail.ticket={id:1,status:'em_atendimento',pet:{name:'Luna'},tutor:{name:'Ana'},veterinarian:{name:'Marina',crmv:'123',uf:'SP'},events:[],context:[],messages:[
   {id:incoming,author_profile:peer,text:'Mensagem recebida',at:1700000000000,...(probe.receivedRead?{read_at:1700000000100}:{})},
   {id:outgoing,author_profile:viewer,text:'Mensagem enviada '+ 'texto '.repeat(160),at:1700000000001,...(probe.peerRead?{read_at:1700000000200}:{})}
  ]};
  queueMicrotask(()=>window.dispatchEvent(new CustomEvent('vettech:support-response',{detail})));
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
   page.clock.install();page.evaluate('('+MOCK+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   page.get_by_role('button',name='Atendimentos',exact=True).click()
   expect(page.locator('.vt-chat-ticket-tutor')).to_have_text('Tutor: Ana')
   page.get_by_role('button',name='Ver conversa',exact=True).click()
   receipt=page.locator('.vt-chat-receipt');expect(receipt).to_have_text('Entregue')
   page.clock.run_for(150);page.clock.fast_forward(21000)
   requests=page.evaluate("probe.requests.filter(r=>r.action==='support_get')")
   assert len(requests)==2 and all('read_through' not in r for r in requests),requests
   page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.querySelector('.vt-chat-messages').scrollTop=0")
   count=page.evaluate('probe.requests.length');page.clock.fast_forward(21000)
   assert page.evaluate('probe.requests.length')==count
   page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
   page.clock.run_for(150);page.clock.fast_forward(21000)
   requests=page.evaluate("probe.requests.filter(r=>r.action==='support_get')")
   assert any(r.get('read_through')=='11111111-1111-4111-8111-111111111111' for r in requests),requests
   expect(receipt).to_have_text('Entregue')
   page.evaluate('probe.peerRead=true');page.clock.fast_forward(21000)
   expect(receipt).to_have_text('Visto')
   count=page.evaluate('probe.requests.length');page.clock.fast_forward(21000)
   assert page.evaluate('probe.requests.length')==count+1
   assert 'read_through' not in page.evaluate("probe.requests.filter(r=>r.action==='support_get').at(-1)")
   page.locator('.vt-chat-messages').evaluate('el=>el.scrollTop=el.scrollHeight')
   page.screenshot(path=str(ROOT/f'openspec/changes/reorganizar-fluxos-chat/evidence/read-receipts-{profile}-{theme}.png'))
   page.close()
  browser.close()
 print('OK: tutor card name, delivered/read, viewport and hidden-tab guards, grouped polling and monotonic acknowledgement in both profiles.')


if __name__=='__main__':main()
