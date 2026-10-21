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
    from datetime import datetime,timedelta
    from pathlib import Path
    from playwright.sync_api import sync_playwright
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    folder=s.folder
    data=s.data
    prefix=data['prefix']
    reason=prefix+'-percurso-navegador'
    checks=[]
    def check(name,value):
     checks.append({'name':name,'passed':bool(value)})
     (folder/'browser-flow.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
     print(json.dumps(checks[-1]),flush=True)
     if not value: raise RuntimeError(name)
    def login(page,actor):
     page.goto(args.app_url)
     page.get_by_label('E-mail',exact=True).fill(data['actors'][actor]['email'])
     page.get_by_label('Senha',exact=True).fill(data['actors'][actor]['password'])
     page.get_by_role('button',name='Login',exact=True).click()
    def logout(page):
     page.get_by_role('button',name='Sair',exact=True).click()
     page.get_by_role('button',name='Login',exact=True).wait_for(timeout=90000)
    with sync_playwright() as p:
     browser=p.chromium.launch(executable_path=args.browser_executable,headless=True)
     page=browser.new_page(viewport={'width':1366,'height':900})
     page.set_default_timeout(90000)
     try:
      login(page,'ta')
      page.get_by_role('button',name='Abrir '+prefix+'-pet-b',exact=True).click()
      page.get_by_role('heading',name=prefix+'-pet-b',exact=True).wait_for()
      page.get_by_role('button',name='Agendar consulta',exact=True).click()
      day=(datetime.now()+timedelta(days=7)).date().isoformat()
      page.get_by_role('button',name=day,exact=True).click()
      page.get_by_label('Horário (08h–17h)',exact=True).fill('10:30')
      page.get_by_role('button',name='Continuar',exact=True).click()
      page.get_by_role('dialog').get_by_role('combobox').nth(0).click()
      page.get_by_role('option',name=prefix+'-pet-a',exact=True).click()
      page.get_by_label('Motivo',exact=True).fill(reason)
      page.get_by_role('dialog').get_by_role('combobox').nth(1).click()
      page.get_by_role('option',name=prefix+'-va',exact=True).click()
      page.get_by_role('button',name='Voltar',exact=True).click()
      page.get_by_role('button',name='Continuar',exact=True).click()
      check('wizard_back_preserves_reason',page.get_by_label('Motivo',exact=True).input_value()==reason)
      check('consent_notice_before_confirm',page.get_by_text('Ao confirmar, você libera previamente',exact=False).is_visible())
      page.get_by_role('button',name='Confirmar agendamento',exact=True).click()
      page.get_by_role('dialog').wait_for(state='hidden')
      check('booking_keeps_global_pet',page.get_by_role('heading',name=prefix+'-pet-b',exact=True).is_visible())
      logout(page)
      login(page,'va')
      page.get_by_role('heading',name='Consultas',exact=True).wait_for()
      card=page.get_by_text(reason,exact=True).locator('..')
      card.get_by_role('button',name='Começar consulta',exact=True).click()
      page.get_by_role('heading',name='Atendimento',exact=True).wait_for()
      page.get_by_label('Diagnóstico',exact=True).fill('Diagnóstico exclusivamente sintético QA')
      page.get_by_role('heading',name='Vacinas',exact=True).locator('..').get_by_role('button',name='Adicionar',exact=True).click()
      page.get_by_label('Vacina',exact=True).fill('Aplicação sintética UI QA')
      page.get_by_label('Lote',exact=True).fill('QA-UI')
      page.get_by_label('Data de aplicação',exact=True).fill(datetime.now().date().isoformat())
      page.get_by_role('button',name='Salvar rascunho',exact=True).click()
      page.get_by_text('Rascunho salvo.',exact=True).wait_for()
      check('draft_saved_from_ui',True)
      page.get_by_role('button',name='Terminar consulta',exact=True).click()
      page.get_by_text('Consulta finalizada. Registros disponíveis ao tutor.',exact=True).wait_for()
      check('finalized_from_ui',True)
      page.get_by_role('button',name='Voltar às consultas',exact=True).click()
      page.get_by_role('heading',name='Consultas',exact=True).wait_for()
      logout(page)
      login(page,'ta')
      page.get_by_role('button',name='Abrir '+prefix+'-pet-a',exact=True).click()
      page.get_by_role('heading',name=prefix+'-pet-a',exact=True).wait_for()
      page.get_by_role('button',name='Vacinas',exact=True).click()
      page.get_by_text('Aplicação sintética UI QA',exact=True).wait_for()
      check('tutor_sees_same_vaccine_in_section',True)
      page.get_by_text('Aplicação sintética UI QA',exact=True).locator('..').get_by_role('button',name='Ver consulta de origem',exact=True).click()
      page.get_by_role('heading',name='Prontuário da consulta',exact=True).wait_for()
      check('consultation_detail_shows_same_vaccine',page.get_by_text('Aplicação sintética UI QA',exact=True).is_visible())
      check('consultation_detail_shows_diagnosis',page.get_by_text('Diagnóstico: Diagnóstico exclusivamente sintético QA',exact=False).is_visible())
      page.set_viewport_size({'width':390,'height':844})
      check('mobile_record_no_overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
      page.screenshot(path=str(folder/'tutor-published-mobile.png'),full_page=True)
     finally:
      page.screenshot(path=str(folder/'flow-last-screen.png'),full_page=True)
      (folder/'flow-last-screen.html').write_text(page.content(),encoding='utf-8')
      browser.close()
      s.discover()


if __name__ == "__main__":
    main()
