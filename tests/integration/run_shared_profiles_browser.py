"""Browser verification using only ephemeral fixtures and a local prod server."""
import argparse
import json
from pathlib import Path
import secrets
import time

from playwright.sync_api import expect, sync_playwright
from run_shared_profiles_live import FIXTURES, Verification, RESET_NAME


def run():
    expect.set_options(timeout=30000)
    data = json.loads(FIXTURES.read_text(encoding='utf-8'))
    assert data['tenant'].startswith('ex')
    verification = Verification(data['tenant'])
    output = Path('.venv/shared-profile-browser-qa')
    output.mkdir(exist_ok=True)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page(viewport={'width':1280,'height':900})
        page.set_default_timeout(30000)
        page.on('pageerror', lambda error: errors.append(str(error)))

        def login(account):
            page.goto('http://localhost:8011/login')
            page.locator('input[name="email"]').fill(account['email'])
            page.locator('input[name="password"]').fill(account['password'])
            page.get_by_role('button',name='Login',exact=True).click()

        def no_overflow():
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'

        login(data['tutor'])
        expect(page.get_by_text('Área do tutor',exact=True)).to_be_visible()
        expect(page.get_by_role('button',name='Novo pet',exact=True)).to_be_visible()
        # The permanent form must no longer occupy Início.
        expect(page.get_by_role('heading',name='Cadastrar pet',exact=True)).to_have_count(0)
        page.get_by_role('button',name='Novo pet',exact=True).click()
        dialog = page.get_by_role('dialog')
        expect(dialog).to_be_visible()
        dialog.get_by_placeholder('Nome do pet',exact=True).fill('Discard this draft')
        page.keyboard.press('Escape')
        expect(dialog).to_have_count(0)
        expect(page.get_by_role('button',name='Novo pet',exact=True)).to_be_focused()
        page.get_by_role('button',name='Novo pet',exact=True).click()
        expect(dialog.get_by_placeholder('Nome do pet',exact=True)).to_have_value('')
        first_name = 'vt-profiles-browser-' + secrets.token_hex(4)
        dialog.get_by_placeholder('Nome do pet',exact=True).fill(first_name)
        dialog.get_by_role('combobox').nth(0).click()
        page.get_by_role('option',name='Cachorro',exact=True).click()
        dialog.get_by_role('button',name='Cadastrar pet',exact=True).click()
        expect(dialog).to_have_count(0)
        first = page.get_by_role('button',name='Abrir '+first_name,exact=True)
        expect(first).to_be_visible()
        first.focus()
        first.press('Enter')
        expect(page.locator('#pet-details').get_by_role('heading',name=first_name,exact=True)).to_be_visible()
        page.get_by_role('button',name='Recolher menu',exact=True).click()
        expect(page.get_by_role('button',name='Expandir menu',exact=True)).to_be_visible()
        expect(page.locator('#pet-details').get_by_role('heading',name=first_name,exact=True)).to_be_visible()
        no_overflow()
        page.screenshot(path=str(output/'desktop.png'),full_page=True)
        page.get_by_role('button',name='Vacinas',exact=True).click()
        expect(page.get_by_text('Esta seção ainda não está disponível.',exact=False)).to_be_visible()
        expect(page.get_by_role('heading',name='Vacinas',exact=True)).to_be_visible()
        page.get_by_role('button',name='Mudar pet',exact=True).click()
        expect(page.get_by_role('button',name='Abrir '+first_name,exact=True)).to_be_visible()
        page.get_by_role('button',name='Abrir '+first_name,exact=True).click()
        time.sleep(21)  # Separate independent journeys under the Xano plan window.
        page.get_by_role('button',name='Novo pet',exact=True).click()
        second_name = 'vt-profiles-browser-' + secrets.token_hex(4)
        dialog.get_by_placeholder('Nome do pet',exact=True).fill(second_name)
        dialog.get_by_role('combobox').nth(0).click()
        page.get_by_role('option',name='Gato',exact=True).click()
        dialog.get_by_role('button',name='Cadastrar pet',exact=True).click()
        expect(dialog).to_have_count(0)
        expect(page.locator('#pet-details').get_by_role('heading',name=first_name,exact=True)).to_be_visible()
        page.set_viewport_size({'width':390,'height':844})
        no_overflow()
        page.get_by_role('button',name='Mudar pet',exact=True).click()
        page.get_by_role('button',name='Abrir '+second_name,exact=True).click()
        expect(page.locator('#pet-details').get_by_role('heading',name=second_name,exact=True)).to_be_visible()
        no_overflow()
        page.screenshot(path=str(output/'mobile.png'),full_page=True)
        page.get_by_role('button',name='Sair',exact=True).click()
        expect(page.locator('input[name="email"]')).to_be_visible()
        time.sleep(21)
        login(data['vet'])
        expect(page.get_by_role('heading',name='Área do veterinário',exact=True)).to_be_visible()
        expect(page.get_by_text(first_name,exact=True)).to_have_count(0)
        page.screenshot(path=str(output/'veterinarian.png'),full_page=True)
        page.get_by_role('button',name='Sair',exact=True).click()
        time.sleep(21)
        page.goto('http://localhost:8011/cadastro')
        # Shared registration changes its fields and loads the real public catalog.
        page.get_by_role('combobox').nth(0).click()
        page.get_by_role('option',name='Veterinário',exact=True).click()
        expect(page.get_by_role('checkbox',name='Cachorro',exact=True)).to_be_visible()
        expect(page.locator('input[name="cpf"]')).to_have_count(0)
        page.locator('input[name="nome"]').fill('Fixture Vet Browser')
        new_email = 'vt-profiles-browser-'+secrets.token_hex(6)+'@example.invalid'
        password = secrets.token_urlsafe(22)
        page.locator('input[name="email"]').fill(new_email)
        page.locator('input[name="telefone"]').fill('11999999999')
        page.locator('input[name="crmv"]').fill('B'+secrets.token_hex(5))
        page.get_by_role('combobox').nth(1).click()
        page.get_by_role('option',name='SP',exact=True).click()
        page.get_by_role('checkbox',name='Cachorro',exact=True).click()
        expect(page.get_by_role('checkbox',name='Cachorro',exact=True)).to_be_checked()
        page.get_by_role('checkbox',name='Clínica geral',exact=True).click()
        expect(page.get_by_role('checkbox',name='Clínica geral',exact=True)).to_be_checked()
        page.locator('input[name="password"]').fill(password)
        page.locator('input[name="password_confirmation"]').fill(password)
        no_overflow()
        page.screenshot(path=str(output/'registration.png'),full_page=True)
        page.get_by_role('button',name='Cadastrar',exact=True).click()
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.get_by_text('Cadastro realizado.',exact=False)).to_be_visible()
        login({'email':new_email,'password':password})
        expect(page.get_by_role('heading',name='Área do veterinário',exact=True)).to_be_visible()
        assert not errors, 'JavaScript errors detected; inspect private browser report'
        page.get_by_role('button',name='Sair',exact=True).click()
        browser.close()
    (output/'result.json').write_text(json.dumps({'desktop_mobile_menu_modal_switch_and_profiles':'passed',
                                                'veterinarian_registration_and_login':'passed','javascript_errors':errors}),encoding='utf-8')
    print('Browser verification passed: keyboard/modal, explicit pet selection, preserved selection after creation, desktop/mobile, shared registration/login and profile isolation.')


def modal_only():
    """Recheck the streamed upload handler and actual double-click behavior."""
    data = json.loads(FIXTURES.read_text(encoding='utf-8'))
    v = Verification(data['tenant'])
    account = v.tutor('modal-check')
    private = Path('.venv/shared-profile-modal-account.json')
    private.write_text(json.dumps(account),encoding='utf-8')
    assert v.request('POST','tutor/signup',account).status_code == 200
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome',headless=True)
            page = browser.new_page(viewport={'width':1280,'height':900})
            expect.set_options(timeout=30000)
            page.goto('http://localhost:8011/login')
            page.locator('input[name="email"]').fill(account['email'])
            page.locator('input[name="password"]').fill(account['password'])
            page.get_by_role('button',name='Login',exact=True).click()
            expect(page.get_by_text('Área do tutor',exact=True)).to_be_visible()
            page.get_by_role('button',name='Novo pet',exact=True).click()
            dialog = page.get_by_role('dialog')
            dialog.get_by_placeholder('Nome do pet',exact=True).fill('vt-profiles-final-modal')
            dialog.get_by_role('combobox').nth(0).click()
            page.get_by_role('option',name='Cachorro',exact=True).click()
            dialog.get_by_role('button',name='Cadastrar pet',exact=True).dblclick()
            expect(dialog).to_have_count(0)
            expect(page.get_by_role('button',name='Abrir vt-profiles-final-modal',exact=True)).to_be_visible()
            page.get_by_role('button',name='Sair',exact=True).click()
            browser.close()
        login=v.request('POST','tutor/login',{k:account[k] for k in ('email','password')}).json()
        pets=v.call('GET',v.origin+'/api:vettech-pets/pets',headers={'Authorization':'Bearer '+login['authToken']})
        assert pets.status_code==200 and len(pets.json())==1, 'Double-click created duplicate pets'
        print('Final streamed modal verification passed: double-click created exactly one pet.')
    finally:
        v.function(RESET_NAME)
    private.unlink(missing_ok=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modal-only',action='store_true')
    args=parser.parse_args()
    modal_only() if args.modal_only else run()
