"""Expiry while editing, server-relative clock, and centered chat start time."""
import argparse
from pathlib import Path
import runpy
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
MOCK=runpy.run_path(str(ROOT/'tests/integration/support_message_actions_browser.py'))['MOCK']


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args()
 mock=MOCK.replace('at:Date.now()-500','at:Date.now()-590000').replace('queueMicrotask(()=>','result.server_time=Date.now();queueMicrotask(()=>')
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=args.chromium)
  page=browser.new_page(viewport={'width':390,'height':844})
  page.route('https://chat.test/**',lambda route:route.fulfill(body=''))
  page.goto('https://chat.test/')
  page.set_content('<div id="vettech-chat-session" data-chat-key="tutor:7"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form><button id="vettech-mascote">Abrir</button>')
  page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'));page.add_style_tag(path=str(ROOT/'assets/support-chat.css'))
  page.clock.install();page.evaluate('('+mock+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
  page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
  expect(page.locator('.vt-chat-start-time')).to_have_count(1)
  page.get_by_role('button',name='Atendimentos',exact=True).click();page.get_by_role('button',name='Ver conversa',exact=True).click()
  expect(page.locator('.vt-chat-start-time')).to_have_count(1)
  page.get_by_role('button',name='Opções da mensagem',exact=True).click()
  page.get_by_role('dialog',name='Opções da mensagem',exact=True).get_by_role('button',name='Editar mensagem',exact=True).click()
  editor=page.get_by_role('textbox',name='Editar mensagem');editor.fill('Rascunho preservado')
  page.clock.set_system_time(page.evaluate('Date.now()')+86400000)
  expect(page.get_by_role('button',name='Salvar alteração',exact=True)).to_be_enabled()
  page.clock.fast_forward(11000)
  expect(page.get_by_role('button',name='Salvar alteração',exact=True)).to_be_disabled()
  expect(editor).to_have_value('Rascunho preservado')
  expect(page.get_by_role('dialog',name='Opções da mensagem',exact=True)).to_contain_text('O prazo de 10 minutos')
  expect(page.locator('.vt-chat-message-menu-trigger')).to_have_count(1)
  assert not page.evaluate("actionProbe.requests.some(r=>['support_edit','support_delete'].includes(r.action))")
  page.get_by_role('button',name='Fechar opções da mensagem',exact=True).click()
  page.get_by_role('button',name='Opções da mensagem',exact=True).click()
  modal=page.get_by_role('dialog',name='Opções da mensagem',exact=True)
  expect(modal.get_by_role('button',name='Editar mensagem',exact=True)).to_be_disabled()
  expect(modal.get_by_role('button',name='Apagar mensagem',exact=True)).to_be_disabled()
  expect(modal).to_contain_text('O prazo de 10 minutos')
  page.screenshot(path=str(ROOT/'openspec/changes/reorganizar-fluxos-chat/evidence/message-window-expired.png'))
  browser.close()
 print('OK: 10-minute expiry disables open editor, preserves draft, ignores local clock jump and keeps one centered start time.')


if __name__=='__main__':main()
