"""Run only against the isolated veterinary_schedule_preview with synthetic data."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://localhost:3038')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1100})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(a.url+'/?secao=horarios')
    expect(page.locator('.vet-schedule-card')).to_have_count(6)
    def verify(theme):
        for status,light,dark,led in [('agendada','rgb(180, 35, 24)','rgb(255, 138, 128)','rgb(255, 82, 82)'),
                ('em_atendimento','rgb(128, 80, 0)','rgb(250, 204, 21)','rgb(250, 204, 21)'),
                ('finalizada','rgb(39, 100, 38)','rgb(156, 237, 117)','rgb(121, 237, 77)')]:
            card=page.locator('.vet-schedule-card--'+status).first;color=light if theme=='light' else dark
            expect(card).to_have_css('border-left-color','rgb(253, 224, 71)' if status=='em_atendimento' else color)
            expect(card.locator('.vet-schedule-pet-name')).to_have_css('color',color)
            expect(card.locator('.vet-schedule-status')).to_have_css('color',color)
            expect(card.locator('.vet-schedule-history-button')).to_have_css('color',color)
            for icon in card.locator('svg:not(.vet-date-led)').all():expect(icon).to_have_css('color',color)
            track=card.locator('.vet-schedule-avatar-led .vet-date-led-track')
            expect(track).to_have_css('stroke',led)
            assert led in track.evaluate('(e)=>getComputedStyle(e).filter')
            start=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset');page.wait_for_timeout(120)
            assert track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')!=start
        expect(page.locator('.vet-schedule-card--finalizada .vet-schedule-start-button')).to_have_count(0)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    verify('light')
    expect(page.locator('[data-appointment-id="1"] img')).to_be_visible()
    expect(page.locator('[data-appointment-id="1"] .consultations-avatar-paw')).to_be_hidden()
    expect(page.locator('[data-appointment-id="2"] .consultations-avatar-paw')).to_be_visible()
    expect(page.locator('[data-appointment-id="5"] button')).to_have_count(0)
    page.screenshot(path=str(a.output/'light.png'),full_page=True)
    page.locator('[data-appointment-id="2"]').get_by_role('button',name='Histórico',exact=True).click()
    expect(page.locator('.attendance-history-dialog')).to_be_visible();page.keyboard.press('Escape')
    page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'dark'}))")
    verify('dark');page.screenshot(path=str(a.output/'dark.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844});verify('dark')
    page.screenshot(path=str(a.output/'mobile.png'),full_page=True)
    page.emulate_media(reduced_motion='reduce')
    for track in page.locator('.vet-schedule-avatar-led .vet-date-led-track').all():expect(track).to_have_css('animation-duration','16s')
    assert not errors,errors
    browser.close()
print('OK: cards Horários vermelho/amarelo/verde, ações, LED/halo, fotos/fallback, histórico e temas/mobile.')
