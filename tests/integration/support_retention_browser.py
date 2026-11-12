"""Retomada real de chamados sintéticos e isolamento ao trocar de conta."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run',required=True)
parser.add_argument('--development',action='store_true',required=True)
parser.add_argument('--url',default='http://localhost:3002')
parser.add_argument('--chromium',default='C:/Program Files/Google/Chrome/Application/chrome.exe')
args=parser.parse_args()
expect.set_options(timeout=60000)
private=(Path('.venv/clinical-smoke')/args.run).resolve()
if not private.is_relative_to(Path('.venv/clinical-smoke').resolve()):raise SystemExit('Ledger fora da pasta de fixtures')
data=json.loads((private/'ledger.json').read_text(encoding='utf-8'))
ticket_id=data['support_tickets'][-1]

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=args.chromium)
    page=browser.new_page();page.set_default_timeout(60000)
    def login(actor):
        page.goto(args.url.rstrip('/')+'/login')
        page.wait_for_function('window.__vetTechChatReady === true')
        page.wait_for_function("document.getElementById('vettech-chat-session')?.dataset.chatKey || document.querySelector('input[name=email]')")
        role='tutor' if actor[0]=='t' else 'veterinario'
        if page.locator('#vettech-chat-session').get_attribute('data-chat-key')==f'{role}:{data["actors"][actor]["id"]}':return
        page.get_by_label('E-mail',exact=True).fill(data['actors'][actor]['email'])
        page.get_by_label('Senha',exact=True).fill(data['actors'][actor]['password'])
        for attempt in range(3):
            page.get_by_role('button',name='Login',exact=True).click()
            try:
                page.wait_for_function("document.getElementById('vettech-chat-session')?.dataset.chatKey",timeout=15000)
                return
            except Exception:
                if attempt<2 and 'limitou temporariamente' in page.locator('body').inner_text():
                    page.wait_for_timeout(20000)
                    continue
                raise
    def open_list():
        page.locator('#vettech-mascote').click()
        page.get_by_role('dialog',name='Assistente Vet Tech').evaluate('el => Promise.all(el.getAnimations().map(a => a.finished))')
        page.get_by_role('button',name='Atendimentos',exact=True).click()
    login('ta');open_list()
    target=f'#{ticket_id} · encerrado · Meu atendimento'
    page.get_by_role('button',name=target,exact=True).click()
    expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_disabled()
    expect(page.get_by_text('Veterinário: Orientação sintética da interface',exact=True)).to_be_visible()
    page.get_by_role('button',name='Fechar chat',exact=True).click()
    expect(page.get_by_role('dialog',name='Assistente Vet Tech')).not_to_be_visible()
    open_list();page.get_by_role('button',name=target,exact=True).click()
    expect(page.get_by_text('Tutor: Mensagem sintética da interface',exact=True)).to_be_visible()
    page.reload();login('ta');open_list()
    page.get_by_role('button',name=target,exact=True).click()
    expect(page.get_by_text('Atendimento encerrado: Verificação sintética concluída',exact=True)).to_be_visible()
    page.get_by_role('button',name='Fechar chat',exact=True).click()
    expect(page.get_by_role('dialog',name='Assistente Vet Tech')).not_to_be_visible()
    page.get_by_role('button',name='Sair',exact=True).first.click()
    page.get_by_role('button',name='Login',exact=True).wait_for()
    login('ta');open_list()
    page.get_by_role('button',name=target,exact=True).click()
    expect(page.get_by_text('Tutor: Mensagem sintética da interface',exact=True)).to_be_visible()
    page.get_by_role('button',name='Fechar chat',exact=True).click()
    expect(page.get_by_role('dialog',name='Assistente Vet Tech')).not_to_be_visible()
    page.get_by_role('button',name='Sair',exact=True).first.click()
    page.get_by_role('button',name='Login',exact=True).wait_for()
    login('tb');open_list()
    expect(page.get_by_text('Nenhum atendimento disponível.',exact=True)).to_be_visible()
    expect(page.get_by_text('Tutor: Mensagem sintética da interface',exact=True)).not_to_be_visible()
    browser.close()
    print('PASS: fechamento, recarga, novo login, encerrado somente leitura e isolamento após troca de conta.')
