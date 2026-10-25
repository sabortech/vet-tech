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
    from playwright.sync_api import sync_playwright,expect
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    folder=s.folder
    checks=[]
    def check(name,value):
     checks.append({'name':name,'passed':bool(value)})
     (folder/'browser-calendar-final.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
     print(json.dumps(checks[-1]),flush=True)
     if not value:raise RuntimeError(name)
    def login(page,actor):
     page.goto(args.app_url)
     page.get_by_label('E-mail',exact=True).fill(s.data['actors'][actor]['email'])
     page.get_by_label('Senha',exact=True).fill(s.data['actors'][actor]['password'])
     page.get_by_role('button',name='Login',exact=True).click()
    with sync_playwright() as p:
     browser=p.chromium.launch(executable_path=args.browser_executable,headless=True)
     page=browser.new_page(viewport={'width':1366,'height':900})
     page.set_default_timeout(90000)
     try:
      login(page,'va')
      page.get_by_role('button',name='Horários',exact=True).click()
      day=page.get_by_label('Dia da agenda',exact=True)
      day.fill('2030-01-01')
      page.get_by_text('Nenhuma consulta neste dia.',exact=True).wait_for()
      check('empty_day_calendar',True)
      page.get_by_role('button',name='Hoje',exact=True).click()
      expect(day).to_have_value(datetime.now().date().isoformat(),timeout=90000)
      check('today_calendar_action',True)
      page.set_viewport_size({'width':390,'height':844})
      check('mobile_veterinary_no_overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
      page.screenshot(path=str(folder/'veterinary-mobile.png'),full_page=True)
      page.set_viewport_size({'width':1366,'height':900})
      page.get_by_role('button',name='Sair',exact=True).click()
      page.get_by_role('button',name='Login',exact=True).wait_for()
      pet=s.data['pets']['c']
      assert pet in s.data['created']['pet']
      _,status=s.store.write('PUT','pet',{'tutor_id':s.data['actors']['ta']['id']},pet)
      assert status==200
      try:
       login(page,'tb')
       page.get_by_role('button',name='Agendar consulta',exact=True).click()
       day=(datetime.now()+timedelta(days=1)).date().isoformat()
       page.get_by_role('button',name=day,exact=True).click()
       page.get_by_label('Horário (08h–17h)',exact=True).fill('09:00')
       page.get_by_role('button',name='Continuar',exact=True).click()
       page.get_by_text('Cadastre um pet em Novo pet antes de confirmar um agendamento.',exact=True).wait_for()
       check('tutor_without_pets_no_fake_option',page.get_by_role('dialog').get_by_role('combobox').count()==0)
       page.keyboard.press('Escape')
      finally:
       s.store.write('PUT','pet',{'tutor_id':s.data['actors']['tb']['id']},pet)
     finally:
      page.screenshot(path=str(folder/'calendar-final-last-screen.png'),full_page=True)
      browser.close()


if __name__ == "__main__":
    main()
