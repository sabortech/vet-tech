"""Run against an isolated preview using synthetic clinical data, never production."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://localhost:3015')
parser.add_argument('--chromium', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.chromium, headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(args.url)
    page.locator('[data-appointment-id="1"]').wait_for()
    assert page.locator('.vet-schedule-card').count() == 6
    assert page.locator('.vet-schedule-hour-label').last.inner_text() == '19:00'
    assert page.locator('.sidebar-navigation button').all_text_contents() == ['Horários', 'Consultas']
    assert 'Não deve aparecer' not in page.locator('[data-appointment-id="5"]').inner_text()
    assert page.locator('[data-appointment-id="5"] button').count() == 0
    assert page.locator('[data-appointment-id="3"]').get_by_role('button', name='Começar consulta').count() == 0
    assert page.locator('[data-appointment-id="2"]').get_by_role('button', name='Retomar').count() == 1
    page.wait_for_timeout(400)  # Let the persisted sidebar preference finish its transition.
    def no_overflow():
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'
        assert page.locator('.vet-schedule-card').evaluate_all('(els)=>els.every(e=>e.scrollWidth <= e.clientWidth + 2)')
    no_overflow()
    page.screenshot(path=str(args.output/'desktop.png'), full_page=True, animations='disabled')
    page.get_by_role('button', name='Recolher menu', exact=True).click()
    page.wait_for_timeout(350)
    assert page.locator('.sidebar--collapsed').count() == 1
    no_overflow()
    page.screenshot(path=str(args.output/'desktop-recolhido.png'), full_page=True)
    page.get_by_role('button', name='Abrir menu', exact=True).filter(visible=True).click()
    def choose_day(value):
        page.get_by_role('button', name='Escolher data', exact=True).click()
        page.get_by_role('dialog').get_by_role('button', name=value, exact=True).click()
        page.get_by_role('dialog').wait_for(state='hidden')
    assert page.locator('input[type="date"]').count() == 0
    page.get_by_role('button', name='Escolher data', exact=True).click()
    dialog = page.get_by_role('dialog')
    dialog.wait_for()
    assert dialog.locator('.vet-date-turtle').count() == 1
    track = dialog.locator('.vet-date-led-track')
    assert track.evaluate('(e)=>getComputedStyle(e).animationName') == 'vet-date-border-orbit'
    assert page.locator('.vet-date-today-button').evaluate('(e)=>getComputedStyle(e).animationName') == 'none'
    assert page.locator('.vet-date-calendar-button').evaluate('(e)=>getComputedStyle(e).animationName') == 'none'
    offset_before = float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px', ''))
    page.wait_for_timeout(150)
    offset_after = float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px', ''))
    assert 0 < (offset_before - offset_after) % 100 < 25, 'Border must rotate clockwise'
    page.keyboard.press('Tab')
    assert dialog.evaluate('(e)=>e.contains(document.activeElement)'), 'Focus must stay in the dialog'
    page.screenshot(path=str(args.output/'calendar-desktop.png'))
    dialog.get_by_role('button', name='Mês anterior', exact=True).click()
    page.keyboard.press('Escape')
    dialog.wait_for(state='hidden')
    page.get_by_role('button', name='Escolher data', exact=True).evaluate('(e)=>{if(document.activeElement!==e)throw new Error("Focus not restored")}')
    results.append('Calendário: foco e Escape, tartaruga, seleção; luz verde gira no sentido horário somente na janela')
    choose_day('2030-01-12')
    page.get_by_text('Seu dia está tranquilo', exact=True).wait_for()
    choose_day('2030-01-13')
    page.get_by_text('Falha simulada ao carregar agenda.', exact=True).wait_for()
    assert page.get_by_text('Seu dia está tranquilo', exact=True).count() == 0
    choose_day('2030-01-11')
    page.locator('[data-appointment-id="1"]').wait_for()
    page.get_by_role('button', name='Próxima', exact=True).click()
    page.get_by_text('Página 2', exact=True).wait_for()
    page.get_by_role('button', name='Anterior', exact=True).click()
    page.locator('[data-appointment-id="1"]').wait_for()
    page.locator('.sidebar-navigation').get_by_role('button', name='Consultas', exact=True).click()
    page.get_by_role('heading', name='Consultas', exact=True).wait_for()
    page.locator('.sidebar-navigation').get_by_role('button', name='Horários', exact=True).click()
    page.locator('[data-appointment-id="1"]').wait_for()
    results.append('Desktop: cards, horas, consentimento, status, menu, vazio, falha, datas, paginação e alternância de seção')
    page.set_viewport_size({'width': 390, 'height': 844})
    page.wait_for_timeout(400)
    no_overflow()
    page.get_by_role('button', name='Abrir menu', exact=True).filter(visible=True).click()
    page.locator('.sidebar--mobile-open').wait_for()
    page.keyboard.press('Escape')
    page.locator('.sidebar--mobile-open').wait_for(state='detached')
    page.screenshot(path=str(args.output/'mobile.png'), full_page=True)
    page.get_by_role('button', name='Escolher data', exact=True).click()
    page.get_by_role('dialog').wait_for()
    page.screenshot(path=str(args.output/'calendar-mobile.png'))
    assert page.get_by_role('dialog').evaluate('(e)=>e.scrollWidth <= e.clientWidth + 2')
    page.evaluate("window.dispatchEvent(new StorageEvent('storage', {key:'vet_tech_theme', newValue:'dark'}))")
    page.wait_for_timeout(200)
    page.screenshot(path=str(args.output/'calendar-mobile-dark.png'))
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.vet-date-led-track').evaluate('(e)=>getComputedStyle(e).animationDuration') == '12s'
    assert page.locator('.vet-date-led-track').evaluate('(e)=>getComputedStyle(e).animationName') == 'vet-date-border-orbit'
    page.keyboard.press('Escape')
    page.get_by_role('dialog').wait_for(state='hidden')
    no_overflow()
    page.screenshot(path=str(args.output/'mobile-escuro.png'), full_page=True)
    results.append('Mobile: sem overflow, drawer/Escape e tema escuro')
    page.goto(args.url+'/tutor')
    page.get_by_role('heading', name='Menu padrão do tutor').wait_for()
    assert page.locator('.sidebar-navigation').get_by_text('Meus Pets', exact=True).count() == 1
    assert page.locator('.sidebar-navigation').get_by_text('Horários', exact=True).count() == 0
    assert not errors, errors
    browser.close()
    results.append('Menu padrão do tutor preservado; nenhuma exceção JavaScript')
(args.output/'browser-results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(results, ensure_ascii=False, indent=2))
