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
    import sys,json
    from pathlib import Path
    from playwright.sync_api import sync_playwright
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    folder=s.folder
    data=s.data
    prefix=data['prefix']
    checks=[]
    def check(name,value):
     checks.append({'name':name,'passed':bool(value)})
     (folder/'browser-final.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
     print(json.dumps(checks[-1]),flush=True)
     if not value:raise RuntimeError(name)
    def login(page,actor):
     page.goto(args.app_url)
     page.get_by_label('E-mail',exact=True).fill(data['actors'][actor]['email'])
     page.get_by_label('Senha',exact=True).fill(data['actors'][actor]['password'])
     page.get_by_role('button',name='Login',exact=True).click()
    with sync_playwright() as p:
     browser=p.chromium.launch(executable_path=args.browser_executable,headless=True)
     page=browser.new_page(viewport={'width':1366,'height':900})
     page.set_default_timeout(90000)
     try:
      login(page,'ta')
      page.get_by_role('button',name='Abrir '+prefix+'-pet-a',exact=True).click()
      page.get_by_role('heading',name=prefix+'-pet-a',exact=True).wait_for()
      page.get_by_role('button',name='Vacinas',exact=True).click()
      page.get_by_text('Aplicação sintética UI QA',exact=True).wait_for()
      page.get_by_text('Aplicação sintética UI QA',exact=True).locator('..').get_by_role('button',name='Ver consulta de origem',exact=True).click()
      page.get_by_role('heading',name='Prontuário da consulta',exact=True).wait_for()
      page.set_viewport_size({'width':390,'height':844})
      page.get_by_role('button',name='Fechar menu',exact=True).click(position={'x':350,'y':300})
      check('mobile_record_no_overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
      page.screenshot(path=str(folder/'tutor-published-mobile.png'),full_page=True)
      page.set_viewport_size({'width':1366,'height':900})
      page.get_by_role('button',name='Sair',exact=True).click()
      page.get_by_role('button',name='Login',exact=True).wait_for()
      login(page,'va')
      page.get_by_role('heading',name='Consultas',exact=True).wait_for()
      page.get_by_role('button',name='Retomar',exact=True).first.click()
      page.get_by_role('heading',name='Atendimento',exact=True).wait_for()
      page.get_by_label('Observações',exact=True).fill('Alteração local sintética não salva')
      page.get_by_role('button',name='Voltar às consultas',exact=True).click()
      page.get_by_role('alertdialog').wait_for()
      check('unsaved_changes_prompt',True)
      page.get_by_role('button',name='Continuar editando',exact=True).click()
      page.get_by_role('alertdialog').wait_for(state='hidden')
      url=page.url
      page.get_by_role('button',name='Voltar às consultas',exact=True).click()
      page.get_by_role('button',name='Descartar e voltar',exact=True).click()
      page.get_by_role('heading',name='Consultas',exact=True).wait_for()
      page.goto(url)
      page.get_by_role('heading',name='Atendimento',exact=True).wait_for()
      check('direct_attendance_url',True)
      check('discard_did_not_save_observations',page.get_by_label('Observações',exact=True).input_value()!='Alteração local sintética não salva')
      page.get_by_role('button',name='Voltar às consultas',exact=True).click()
      page.get_by_role('button',name='Horários',exact=True).click()
      page.get_by_label('Dia da agenda',exact=True).wait_for()
      page.get_by_label('Dia da agenda',exact=True).fill('2030-01-01')
      page.get_by_role('button',name='Hoje',exact=True).click()
      page.wait_for_function("document.getElementById('agenda-day').value !== '2030-01-01'",timeout=90000)
      check('today_calendar_action',page.get_by_label('Dia da agenda',exact=True).input_value()!='2030-01-01')
      page.set_viewport_size({'width':390,'height':844})
      check('mobile_veterinary_no_overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
      page.screenshot(path=str(folder/'veterinary-mobile.png'),full_page=True)
     finally:
      page.screenshot(path=str(folder/'final-last-screen.png'),full_page=True)
      (folder/'final-last-screen.html').write_text(page.content(),encoding='utf-8')
      browser.close()


if __name__ == "__main__":
    main()
