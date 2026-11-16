"""Verifica a interface local sem enviar códigos, cadastrar ou alterar senhas.

Etapas protegidas são simuladas SOMENTE no navegador isolado via delta visual;
não cria autorização nem modifica o State do servidor. Login de Configurações
usa exclusivamente fixtures sintéticas .invalid, sem escrita nas contas.
"""
import argparse
import json
import re
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vet_tech.features.auth.state import State
from vet_tech.features.settings.state import SettingsState

DUMMY = 'Somente-ensaio-visual-42!'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:3000')
    parser.add_argument('--chromium', default='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome')
    parser.add_argument('--output', type=Path, default=ROOT/'openspec/changes/verificar-alteracao-senha-email/evidence/password-visibility')
    parser.add_argument('--back-only', action='store_true', help='Regressão de Voltar sem chamadas ao Xano.')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    checks, errors, leaks = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])

        def new_page():
            context = browser.new_context(viewport={'width': 1440, 'height': 1000})
            page = context.new_page()
            sockets = []
            page.on('pageerror', lambda _: errors.append('Erro JavaScript no navegador.'))
            def socket(route):
                sockets.append(route)
                route.connect_to_server()
            page.route_web_socket('**/_event/**', socket)
            def watch(ws):
                ws.on('framesent', lambda message: leaks.append('Valor de ensaio enviado por websocket.') if DUMMY in str(message) else None)
            page.on('websocket', watch)
            page.goto(args.url+'/login', wait_until='domcontentloaded')
            expect(page.locator('#login-password')).to_be_visible(timeout=60000)
            page.wait_for_function('!!window.__reflex')
            return context, page, sockets

        def inject(sockets, state, **values):
            # Fixture visual: o servidor não recebe esse delta e nenhum grant existe.
            delta = {state.get_full_name(): {key+'_rx_state_': value for key, value in values.items()}}
            sockets[-1].send('42/_event,'+json.dumps(['event', {'delta': delta}]))

        def check_field(page, field_id):
            field = page.locator('#'+field_id)
            button = page.locator('[data-password-target="'+field_id+'"]')
            expect(field).to_have_attribute('type', 'password')
            expect(button).to_have_attribute('type', 'button')
            expect(button).to_have_attribute('aria-controls', field_id)
            field.fill(DUMMY)
            button.focus()
            button.press('Enter')
            expect(field).to_have_attribute('type', 'text')
            expect(button).to_have_attribute('aria-pressed', 'true')
            expect(button).to_have_attribute('aria-label', re.compile('^Ocultar '))
            assert field.input_value() == DUMMY
            expect(button.locator('.password-eye-open')).to_be_visible()
            button.press('Space')
            expect(field).to_have_attribute('type', 'password')
            expect(button).to_have_attribute('aria-pressed', 'false')
            assert field.input_value() == DUMMY
            # Reset nativo deve ocultar a senha e restaurar o rótulo acessível.
            button.click()
            field.evaluate('(e)=>e.form.reset()')
            expect(field).to_have_attribute('type', 'password')
            expect(button).to_have_attribute('aria-pressed', 'false')
            checks.append(field_id+': teclado, valor preservado, ícone e reset')

        def screenshots(page, name):
            for width in (1440, 390):
                page.set_viewport_size({'width': width, 'height': 1000})
                for theme in ('light', 'dark'):
                    page.evaluate("(value)=>window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:value}))", theme)
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                    for button in page.locator('[data-password-target]').all():
                        field = page.locator('#'+button.get_attribute('data-password-target'))
                        a = button.bounding_box()
                        b = field.evaluate('(e)=>e.closest(".password-control,.settings-control").getBoundingClientRect().toJSON()')
                        assert a and b and a['x'] >= b['x'] and a['x']+a['width'] <= b['x']+b['width']+1
                    page.screenshot(path=str(args.output/f'{name}-{width}-{theme}.png'), full_page=True)
            checks.append(name+': temas e 390/1440 px sem overflow')

        context, page, sockets = new_page()
        if args.back_only:
            for width in (1440, 390):
                page.set_viewport_size({'width': width, 'height': 1000})
                page.get_by_role('button', name='Esqueceu a senha?', exact=True).click()
                email = page.get_by_label('E-mail cadastrado', exact=True)
                expect(email).to_be_visible()
                email.fill('local-only@example.invalid')
                page.get_by_role('button', name='Voltar', exact=True).click()
                expect(page.locator('#login-password')).to_be_visible()
                page.get_by_role('button', name='Esqueceu a senha?', exact=True).click()
                expect(page.get_by_label('E-mail cadastrado', exact=True)).to_have_value('')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.screenshot(path=str(args.output/f'back-reopened-{width}.png'), full_page=True)
                page.get_by_role('button', name='Cancelar', exact=True).click()
                expect(page.locator('#login-password')).to_be_visible()
                checks.append(f'Voltar/{width}: login restaurado e e-mail limpo ao reabrir')
            context.close()
            browser.close()
            (args.output/'back-results.json').write_text(json.dumps({'checks': checks, 'page_errors': errors, 'xano_calls': 0}, ensure_ascii=False, indent=2))
            assert not errors
            print('PASS: Voltar retorna ao login e limpa a recuperação em desktop/celular, sem chamadas ao Xano.')
            return
        check_field(page, 'login-password')
        screenshots(page, 'login')
        page.get_by_role('button', name='Esqueceu a senha?', exact=True).click()
        expect(page.get_by_label('E-mail cadastrado', exact=True)).to_be_visible()
        page.get_by_label('E-mail cadastrado', exact=True).fill('local-only@example.invalid')
        page.get_by_role('button', name='Voltar', exact=True).click()
        expect(page.locator('#login-password')).to_be_visible()
        page.get_by_role('button', name='Esqueceu a senha?', exact=True).click()
        expect(page.get_by_label('E-mail cadastrado', exact=True)).to_have_value('')
        checks.append('Voltar na primeira etapa retorna ao login e limpa o e-mail')
        title = page.get_by_role('heading', name='Recupere seu acesso', exact=True)
        expect(title).to_be_visible()
        brand = page.get_by_text('Vet Tech Team', exact=True)
        mascot = page.get_by_alt_text('Tartaruga Vet Tech com os braços em V', exact=True)
        expect(mascot).to_be_visible()
        assert mascot.evaluate('(e)=>e.complete && e.naturalWidth>0')
        assert brand.bounding_box()['y'] < mascot.bounding_box()['y'] < title.bounding_box()['y']
        screenshots(page, 'recovery-brand')
        inject(sockets, State, recovery_step='password')
        expect(page.locator('#recovery-new_password')).to_be_visible()
        check_field(page, 'recovery-new_password')
        check_field(page, 'recovery-password_confirmation')
        first = page.locator('#recovery-new_password')
        first.fill(DUMMY)
        page.locator('[data-password-target="recovery-new_password"]').click()
        expect(page.locator('#recovery-password_confirmation')).to_have_attribute('type', 'password')
        page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));delete document.hidden")
        expect(first).to_have_attribute('type', 'password')
        first.evaluate('(e)=>e.form.reset()')
        screenshots(page, 'recovery-password-visual-fixture')
        page.get_by_role('button', name='Cancelar', exact=True).click()
        expect(page.locator('#login-password')).to_have_attribute('type', 'password')
        checks.append('recuperação: campos independentes, ocultar página e cancelar')
        page.goto(args.url+'/cadastro', wait_until='domcontentloaded')
        expect(page.locator('#signup-password')).to_be_visible(timeout=30000)
        for role in ('Tutor', 'Veterinário'):
            page.get_by_role('combobox').first.click()
            page.get_by_role('option', name=role, exact=True).click()
            check_field(page, 'signup-password')
            check_field(page, 'signup-password-confirmation')
            screenshots(page, 'signup-'+('tutor' if role=='Tutor' else 'vet'))
        context.close()

        cfg = json.loads((ROOT/'.env.foundation-fixtures.json').read_text())
        assert cfg['synthetic'] is True and cfg['environment']=='development'
        for actor in ('tutor_b', 'vet_b'):
            cred = cfg['identity_credentials'][actor]
            assert cred['email'].endswith('.invalid')
            context, page, sockets = new_page()
            page.get_by_label('E-mail', exact=True).fill(cred['email'])
            page.locator('#login-password').fill(cred['password'])
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page.locator('#vet-tech-sidebar')).to_be_visible(timeout=60000)
            page.goto(args.url+'/configuracoes', wait_until='domcontentloaded')
            # A fixture visual não deve disputar com o carregamento da conta.
            expect(page.locator('#settings-nome')).to_be_enabled(timeout=60000)
            page.get_by_role('tab', name='Segurança', exact=True).click(timeout=60000)
            expect(page.locator('#current_password')).to_be_visible(timeout=30000)
            check_field(page, 'current_password')
            inject(sockets, SettingsState, password_code_sent=True)
            expect(page.locator('#new_password')).to_be_visible()
            for field_id in ('current_password', 'new_password', 'password_confirmation'):
                check_field(page, field_id)
            screenshots(page, 'settings-'+actor+'-visual-fixture')
            context.close()
        browser.close()
    result = {'checks': checks, 'page_errors': errors, 'test_value_network_leaks': leaks,
              'protected_stages': 'client-only visual fixtures; no email, signup, recovery verification or password write performed'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    assert not errors and not leaks
    print('PASS:',len(checks),'verificações de interface; sem e-mails, cadastros ou alterações de senha.')


if __name__ == '__main__':
    main()
