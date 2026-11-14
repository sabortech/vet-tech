"""Local emoji picker in assistant and human chat; simulated bridge only."""
import argparse
from pathlib import Path
import runpy
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[2]
MOCK=runpy.run_path(str(ROOT/'tests/integration/chat_flows_browser.py'))['MOCK']


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args()
 mock=MOCK.replace("status:d.action==='support_close'?'encerrado':'aguardando'", "status:d.action==='support_close'?'encerrado':(window.ticketStatus||'em_atendimento')")
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=args.chromium)
  for profile,theme,width in [('', 'light',320),('tutor','dark',390),('veterinario','light',1366)]:
   page=browser.new_page(viewport={'width':width,'height':900})
   page.route('https://chat.test/**',lambda route:route.fulfill(body=(ROOT/'assets'/route.request.url.split('chat.test/')[1]).read_bytes()) if (ROOT/'assets'/route.request.url.split('chat.test/')[1]).is_file() else route.fulfill(body=''))
   page.goto('https://chat.test/')
   key=profile+':7' if profile else ''
   page.set_content(f'<div id="vettech-chat-session" data-chat-key="{key}"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form><button id="vettech-mascote">Abrir</button>')
   page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'));page.add_style_tag(path=str(ROOT/'assets/support-chat.css'))
   page.evaluate('theme=>document.documentElement.dataset.vtTheme=theme',theme)
   page.evaluate('('+mock+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   chat=page.locator('#vettech-support-chat');field=page.get_by_role('textbox',name='Digite sua pergunta')
   toggle=page.get_by_role('button',name='Abrir emojis',exact=True);panel=page.get_by_role('dialog',name='Emojis',exact=True)
   field.fill('Olá mundo');field.evaluate('el=>el.setSelectionRange(4,9)')
   count=page.evaluate('probe.requests.length')
   toggle.click();expect(panel).to_be_visible()
   page.get_by_role('searchbox',name='Buscar emoji').fill('cachorro')
   page.get_by_role('button',name='cachorro',exact=True).click()
   expect(field).to_have_value('Olá 🐶');expect(field).to_be_focused();expect(panel).not_to_be_visible()
   assert page.evaluate('probe.requests.length')==count
   toggle.click();page.get_by_role('searchbox',name='Buscar emoji').fill('coracao')
   expect(page.get_by_role('button',name='coração vermelho',exact=True)).to_be_visible()
   page.keyboard.press('Escape');expect(panel).not_to_be_visible();expect(chat).to_be_visible();expect(toggle).to_be_focused()
   field.fill('a'*1000);toggle.click();page.get_by_role('button',name='sorriso',exact=True).click()
   expect(panel).to_contain_text('Limite de 1000 caracteres atingido.');expect(field).to_have_value('a'*1000)
   page.get_by_role('button',name='Fechar emojis',exact=True).click()
   field.fill('Olá ');toggle.click();page.get_by_role('combobox',name='Categoria de emojis').select_option('Pets')
   page.screenshot(path=str(ROOT/f'openspec/changes/reorganizar-fluxos-chat/evidence/emojis-assistant-{profile or "guest"}-{theme}.png'))
   page.get_by_role('button',name='patinhas',exact=True).click();expect(field).to_have_value('Olá 🐾')
   toggle.click();field.click();expect(panel).not_to_be_visible()
   if profile:
    page.get_by_role('button',name='Atendimentos',exact=True).click();page.get_by_role('button',name='Ver conversa',exact=True).click()
    expect(toggle).to_be_enabled();field.fill('Tudo bem ');toggle.click();page.get_by_role('button',name='positivo',exact=True).click()
    expect(field).to_have_value('Tudo bem 👍')
    page.get_by_role('button',name='Enviar mensagem',exact=True).click()
    assert page.evaluate("probe.requests.filter(r=>r.action==='support_send').at(-1).message")=='Tudo bem 👍'
    toggle.click();page.screenshot(path=str(ROOT/f'openspec/changes/reorganizar-fluxos-chat/evidence/emojis-human-{profile}-{theme}.png'))
    page.keyboard.press('Escape')
    page.evaluate("window.ticketStatus='aguardando'")
    page.get_by_role('button',name='Informações do atendimento: Em atendimento',exact=True).click()
    page.get_by_role('button',name='Atualizar atendimento',exact=True).click();page.get_by_role('button',name='Fechar informações do atendimento',exact=True).click()
    expect(toggle).to_be_disabled();expect(panel).not_to_be_visible()
   assert page.locator('.vt-chat-form').evaluate('el=>el.scrollWidth<=el.clientWidth')
   page.close()
  browser.close()
 print('OK: emojis for guest, tutor and veterinarian; cursor, search, category, limit, Escape, disabled state and no extra requests.')


if __name__=='__main__':main()
