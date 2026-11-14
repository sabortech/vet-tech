"""Regression: recipient reads then switches tabs before the 20s poll."""
import argparse
import copy
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
MID='11111111-1111-4111-8111-111111111111'
BOOT=r"""() => {
 window.__vetTechChatReady=true;
 document.addEventListener('submit',async event=>{
  if(event.target.id!=='vettech-chat-bridge')return;event.preventDefault();
  const d=JSON.parse(document.getElementById('vettech-chat-payload').value);
  const data=await window.testSupportTransport(d);
  if(data)window.dispatchEvent(new CustomEvent('vettech:support-response',{detail:{...data,request_id:d.request_id,conversation_id:d.conversation_id,ok:true}}));
 });
}"""


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args()
 messages=[{'id':MID,'author_profile':'veterinario','text':'Olá, tudo bem?','at':1700000000000}]
 calls=[]
 def transport(data):
  calls.append(copy.deepcopy(data))
  if not data['action'].startswith('support_'):return None
  if data.get('read_through')==MID and data['session_key'].startswith('tutor:'):
   messages[0].setdefault('read_at',1700000000100)
  if data['action']=='support_list':return {'tickets':[{'id':1,'own':True,'status':'em_atendimento','tutor':{'name':'Ana'}}]}
  return {'ticket':{'id':1,'status':'em_atendimento','pet':{'name':'Luna'},'tutor':{'name':'Ana'},'veterinarian':{'name':'Marina','crmv':'123','uf':'SP'},'messages':copy.deepcopy(messages),'context':[],'events':[]}}
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=args.chromium)
  context=browser.new_context(viewport={'width':390,'height':844})
  def open_chat(profile):
   page=context.new_page()
   page.route('https://chat.test/**',lambda route:route.fulfill(body=''))
   page.goto('https://chat.test/')
   page.set_content(f'<div id="vettech-chat-session" data-chat-key="{profile}:7"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form><button id="vettech-mascote">Abrir</button>')
   page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'));page.add_style_tag(path=str(ROOT/'assets/support-chat.css'))
   page.evaluate("document.documentElement.dataset.vtTheme='dark'")
   page.expose_function('testSupportTransport',transport)
   page.evaluate('('+BOOT+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   page.get_by_role('button',name='Atendimentos',exact=True).click();page.get_by_role('button',name='Ver conversa',exact=True).click()
   return page
  sender=open_chat('veterinario');expect(sender.locator('.vt-chat-receipt')).to_have_text('Entregue')
  sender.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});Object.defineProperty(document,'hasFocus',{configurable:true,value:()=>false});window.dispatchEvent(new Event('blur'))")
  recipient=open_chat('tutor');recipient.bring_to_front();recipient.wait_for_function('document.hasFocus()')
  expect(recipient.locator('.vt-chat-bubble p').filter(has_text='Olá, tudo bem?')).to_be_visible()
  recipient.wait_for_timeout(100)
  recipient.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});Object.defineProperty(document,'hasFocus',{configurable:true,value:()=>false});window.dispatchEvent(new Event('blur'));document.dispatchEvent(new Event('visibilitychange'))")
  sender.bring_to_front()
  sender.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});Object.defineProperty(document,'hasFocus',{configurable:true,value:()=>true});document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('focus'))")
  try:
   expect(sender.locator('.vt-chat-receipt')).to_have_text('Visto',timeout=8000)
  except AssertionError:
   print('calls',[(c['session_key'],c['action'],bool(c.get('read_through'))) for c in calls])
   print('read',bool(messages[0].get('read_at')),'focus',sender.evaluate('document.hasFocus()'),recipient.evaluate('document.hasFocus()'))
   raise
  expect(sender.locator('.vt-chat-receipt>.vt-chat-icon svg')).to_have_count(1)
  assert sender.locator('.vt-chat-receipt>.vt-chat-icon').evaluate('el=>el.getBoundingClientRect().width')==16
  assert messages[0].get('read_at')
  reads=[c for c in calls if c.get('read_through')==MID]
  assert len(reads)==1,reads
  assert all(c['session_key'].startswith('tutor:') for c in reads)
  sender.screenshot(path=str(ROOT/'openspec/changes/reorganizar-fluxos-chat/evidence/read-seen-fast-tab-switch.png'))
  browser.close()
 print('OK: shared two-tab state changes Entregue to Visto after a quick profile switch, with one grouped read acknowledgement.')


if __name__=='__main__':main()
