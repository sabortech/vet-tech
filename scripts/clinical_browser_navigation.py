"""Explicit synthetic-fixture verification; read deployment-review.md before use.
Tokens, records and screenshots remain in the private run directory.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--app-url', default='http://localhost:8000')
    parser.add_argument('--browser-executable', default='C:/Program Files/Google/Chrome/Application/chrome.exe')
    args = parser.parse_args()
    from clinical_smoke import PRIVATE
    import json
    from pathlib import Path
    from playwright.sync_api import sync_playwright

    folder=PRIVATE/args.run
    if not folder.resolve().is_relative_to(PRIVATE.resolve()):
        raise RuntimeError("Run must stay inside the private fixture directory")
    ledger=json.loads((folder/'ledger.json').read_text(encoding='utf-8'))
    checks=[]
    def check(name,value):
        checks.append({'name':name,'passed':bool(value)})
        (folder/'browser-result.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
        print(json.dumps(checks[-1]),flush=True)
        if not value: raise RuntimeError('Browser check failed: '+name)

    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser_executable,headless=True)
        page=browser.new_page(viewport={'width':1366,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(args.app_url)
        page.get_by_label('E-mail',exact=True).fill(ledger['actors']['ta']['email'])
        page.get_by_label('Senha',exact=True).fill(ledger['actors']['ta']['password'])
        page.get_by_role('button',name='Login',exact=True).click()
        page.get_by_role('button',name='Agendar consulta',exact=True).wait_for(timeout=90000)
        check('dashboard_without_global_pet',page.get_by_text('Escolha um pet para continuar',exact=False).is_visible())
        page.get_by_role('button',name='Agendar consulta',exact=True).click()
        page.get_by_role('dialog').wait_for()
        check('booking_step_one',page.get_by_text('Etapa 1 de 2',exact=False).is_visible())
        page.keyboard.press('Escape')
        page.get_by_role('dialog').wait_for(state='hidden')
        check('cancel_returns_focus',page.get_by_role('button',name='Agendar consulta',exact=True).evaluate('(e)=>e===document.activeElement'))
        page.set_viewport_size({'width':390,'height':844})
        page.get_by_role('button',name='Fechar menu',exact=True).click(position={'x':350,'y':300})
        check('mobile_dashboard_no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
        page.get_by_role('button',name='Agendar consulta',exact=True).click()
        check('mobile_dialog_fits',page.get_by_role('dialog').bounding_box()['width']<=390)
        page.keyboard.press('Escape')
        page.get_by_role('button',name='Sair',exact=True).click()
        page.get_by_role('button',name='Login',exact=True).wait_for(timeout=60000)
        page.set_viewport_size({'width':1366,'height':900})
        page.get_by_label('E-mail',exact=True).fill(ledger['actors']['va']['email'])
        page.get_by_label('Senha',exact=True).fill(ledger['actors']['va']['password'])
        page.get_by_role('button',name='Login',exact=True).click()
        page.get_by_role('heading',name='Consultas',exact=True).wait_for(timeout=90000)
        page.get_by_role('button',name='Horários',exact=True).click()
        page.get_by_label('Dia da agenda',exact=True).wait_for()
        check('vertical_calendar',page.get_by_label('Calendário vertical de consultas',exact=True).is_visible())
        check('browser_no_runtime_error',not errors)
        page.screenshot(path=str(folder/'veterinary-desktop.png'),full_page=True)
        browser.close()



if __name__ == "__main__":
    main()
