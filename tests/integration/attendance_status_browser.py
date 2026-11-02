"""Synthetic attendance_completion_preview only. No production patient data."""
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
    page.add_init_script("""
        localStorage.setItem('vet_tech_theme','light');
        // Chromium may report a deferred ResizeObserver notification during resize.
        // This Reflex version dereferences ErrorEvent.error even when it is null.
        // Keep this guard in the synthetic harness, not the production application.
        window.addEventListener('error', event=>{
            if(event.error===null)console.warn('Native browser notification: '+event.message);
            if(event.error===null && (event.message==='ResizeObserver loop completed with undelivered notifications.' || event.message==='ResizeObserver loop limit exceeded'))event.stopImmediatePropagation();
        },true);
    """)
    page.on('console',lambda message: print(message.text,flush=True) if message.text.startswith('Native browser notification:') else None)
    errors=[]
    def record_error(e):
        errors.append(e.stack)
        print(e.stack,flush=True)
    page.on('pageerror',record_error)
    page.goto(a.url+'/atendimento/43')
    expect(page.locator('.attendance-page--em_atendimento')).to_be_visible()
    def verify_led(color,reduced=False):
        panel=page.locator('.attendance-glass');svg=panel.locator('.attendance-form-led');track=svg.locator('rect')
        expect(track).to_have_css('stroke',color)
        expect(svg).to_have_css('pointer-events','none')
        assert color in track.evaluate('(e)=>getComputedStyle(e).filter')
        expect(track).to_have_css('animation-name','vet-date-border-orbit')
        expect(track).to_have_css('animation-duration','12s' if reduced else '6s')
        start=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset');page.wait_for_timeout(150)
        assert start!=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
        frames=track.evaluate('(e)=>e.getAnimations()[0].effect.getKeyframes().map(f=>f.strokeDashoffset)')
        assert float(frames[-1].replace('px',''))==-100
        x,y=panel.bounding_box(),svg.bounding_box()
        assert abs(x['width']-y['width'])<=3 and abs(x['height']-y['height'])<=3,(x,y)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    def check_portal(selector):
        portal=page.locator(selector)
        expect(portal).to_be_visible()
        tokens=portal.evaluate("e=>['--vet-primary','--vet-surface','--vet-text'].map(k=>getComputedStyle(e).getPropertyValue(k).trim())")
        assert all(tokens),tokens
        assert tokens[0] in ('#805000','#facc15'),tokens
    page.locator('#clinic-diagnostico').fill('Rascunho sintético preservado')
    verify_led('rgb(250, 204, 21)')
    before=page.locator('.attendance-glass').bounding_box()['height']
    page.locator('.attendance-record-card').first.get_by_role('button',name='Adicionar',exact=True).click()
    page.wait_for_function("before=>document.querySelector('.attendance-glass').getBoundingClientRect().height>before",arg=before)
    verify_led('rgb(250, 204, 21)')
    page.screenshot(path=str(a.output/'yellow-light.png'),full_page=True)
    for theme in ('light','dark'):
        page.evaluate("theme=>{localStorage.setItem('vet_tech_theme',theme);window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:theme}))}",theme)
        verify_led('rgb(250, 204, 21)')
        page.get_by_role('button',name='Consultar histórico anterior',exact=True).click()
        check_portal('.attendance-history-dialog');page.keyboard.press('Escape')
        expect(page.locator('.attendance-history-dialog')).to_be_hidden()
        page.get_by_role('button',name='Data do atendimento',exact=True).click()
        check_portal('.attendance-date-dialog')
        expect(page.locator('.attendance-date-dialog .vet-date-led-track')).to_have_css('stroke','rgb(250, 204, 21)')
        page.get_by_role('combobox',name='Mês do calendário').click()
        check_portal('.attendance-date-select-menu');page.keyboard.press('Escape')
        expect(page.locator('.attendance-date-select-menu')).to_be_hidden()
        page.get_by_role('button',name='Voltar sem alterar',exact=True).click()
        expect(page.locator('.attendance-date-dialog')).to_be_hidden()
        expect(page.locator('#clinic-diagnostico')).to_have_value('Rascunho sintético preservado')
        page.screenshot(path=str(a.output/(theme+'.png')),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.emulate_media(reduced_motion='reduce');verify_led('rgb(250, 204, 21)',True)
    page.screenshot(path=str(a.output/'mobile.png'),full_page=True)
    for status,color in [('agendada','rgb(255, 82, 82)'),('finalizada','rgb(121, 237, 77)')]:
        page.goto(a.url+'/atendimento/43?status='+status)
        expect(page.locator('.attendance-page--'+status)).to_be_visible()
        verify_led(color,True)
        page.screenshot(path=str(a.output/(status+'.png')),full_page=True)
    assert not errors,errors
    browser.close()
print('OK: Atendimento por status, LED completo/halo horário, altura dinâmica, temas/mobile, histórico/calendário e rascunho.')
