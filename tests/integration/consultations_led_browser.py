"""Verify real SVG animation with VET_TECH_PREVIEW_LED=1 synthetic preview only."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://localhost:3038')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(args.url+'/?secao=consultas')
    expect(page.locator('.consultations-card')).to_have_count(5)

    def verify_palette(card):
        # Compare actual rendered elements, including text contrast on solid actions.
        result=card.evaluate("""(root)=>{
            const ctx=document.createElement('canvas').getContext('2d');
            const rgb=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return Array.from(ctx.getImageData(0,0,1,1).data).slice(0,3)};
            const same=(a,b)=>rgb(a).every((v,i)=>Math.abs(v-rgb(b)[i])<2);
            const style=getComputedStyle(root),accent=style.getPropertyValue('--consultation-accent').trim();
            const luminance=c=>rgb(c).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
            const contrast=(a,b)=>{a=luminance(a);b=luminance(b);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
            const errors=[];
            for(const icon of root.querySelectorAll('svg:not(.vet-date-led)'))
                if(!same(getComputedStyle(icon).color,accent))errors.push('icon palette');
            for(const name of root.querySelectorAll('.consultations-pet-name'))
                if(!same(getComputedStyle(name).color,accent))errors.push('name palette');
            for(const button of root.querySelectorAll('.consultations-start')){
                const c=getComputedStyle(button);
                if(contrast(c.color,c.backgroundColor)<4.5)errors.push('action contrast');
                if(!same(c.backgroundColor,style.getPropertyValue('--consultation-action').trim()))errors.push('action palette');
            }
            for(const button of root.querySelectorAll('.consultations-history')){
                const c=getComputedStyle(button);
                if(!same(c.color,accent)||!same(c.borderTopColor,accent))errors.push('history palette');
                if(c.boxShadow==='none'||!c.boxShadow.includes(c.color))errors.push('history visible outline palette');
            }
            for(const badge of root.querySelectorAll('.consultations-status')){
                const c=getComputedStyle(badge);
                if(contrast(c.color,c.backgroundColor)<4.5)errors.push('badge contrast');
            }
            return errors;
        }""")
        assert not result,result
        for avatar in card.locator('.consultations-avatar').all():
            if avatar.locator('img').count():expect(avatar.locator('.consultations-avatar-paw')).to_be_hidden()
            else:expect(avatar.locator('.consultations-avatar-paw')).to_be_visible()

    def verify(status,color):
        card=page.locator('.consultations-card--'+status).first
        track=card.locator('.consultations-status-led .vet-date-led-track')
        expect(track).to_have_count(1)
        expect(track).to_have_css('stroke',color)
        shadow=track.evaluate('(e)=>getComputedStyle(e).filter')
        assert shadow.count('drop-shadow')==3, shadow
        assert color in shadow, shadow
        assert track.evaluate('(e)=>getComputedStyle(e).animationName')=='vet-date-border-orbit'
        # Negative dash offset advances a standard SVG rect clockwise.
        frames=track.evaluate('(e)=>e.getAnimations()[0].effect.getKeyframes().map(f=>f.strokeDashoffset)')
        assert float(frames[0].replace('px',''))==0 and float(frames[-1].replace('px',''))==-100,frames
        start=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
        page.wait_for_timeout(150)
        assert track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')!=start
        svg=card.locator('.consultations-status-led')
        expect(svg).to_have_attribute('aria-hidden','true')
        expect(svg).to_have_css('pointer-events','none')
        expect(svg).to_have_css('overflow','visible')
        a,b=card.bounding_box(),svg.bounding_box()
        assert abs(a['width']-b['width'])<=3 and abs(a['height']-b['height'])<=3,(a,b)
        verify_palette(card)
        return card

    def verify_summary(color):
        summary=page.locator('.consultations-summary')
        selected=page.locator('.consultations-card.is-selected')
        expect(selected).to_have_count(1)
        # Compare after both loading and the card's background transition settle.
        page.wait_for_function("""()=>{
            const card=document.querySelector('.consultations-card.is-selected');
            const summary=document.querySelector('.consultations-summary');
            if(!card||!summary||summary.getAttribute('aria-busy')==='true')return false;
            const a=getComputedStyle(card), b=getComputedStyle(summary);
            return a.backgroundColor===b.backgroundColor && a.borderTopColor===b.borderTopColor;
        }""")
        track=summary.locator('.consultations-status-led .vet-date-led-track')
        expect(track).to_have_count(1)
        expect(track).to_have_css('stroke',color)
        assert color in track.evaluate('(e)=>getComputedStyle(e).filter')
        start=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
        page.wait_for_timeout(150)
        assert track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')!=start
        verify_palette(summary)
        expect(summary.locator('.consultations-status-led')).to_have_css('pointer-events','none')
        a,b=summary.bounding_box(),summary.locator('.consultations-status-led').bounding_box()
        assert abs(a['width']-b['width'])<=3 and abs(a['height']-b['height'])<=3,(a,b)

    expect(page.locator('.consultations-summary .consultations-status-led')).to_have_count(0)
    scheduled=verify('agendada','rgb(255, 82, 82)')
    scheduled.locator('.consultations-patient-button').click()
    verify_summary('rgb(255, 82, 82)')
    active=verify('em_atendimento','rgb(250, 204, 21)')
    # The overlay must not steal clicks or alter the existing authorized flow.
    active.locator('.consultations-patient-button').click()
    expect(page.locator('.consultations-summary')).to_contain_text('Alergias não informadas')
    verify_summary('rgb(250, 204, 21)')
    active.get_by_role('button',name='Ver prontuário',exact=True).click()
    expect(page.locator('.attendance-history-dialog')).to_be_visible()
    page.keyboard.press('Escape')
    page.screenshot(path=str(args.output/'pending-in-progress-light.png'))
    page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'dark'}))")
    verify('agendada','rgb(255, 82, 82)');verify('em_atendimento','rgb(250, 204, 21)')
    verify_summary('rgb(250, 204, 21)')
    page.screenshot(path=str(args.output/'pending-in-progress-dark.png'))
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    verify('agendada','rgb(255, 82, 82)')
    verify_summary('rgb(250, 204, 21)')
    page.screenshot(path=str(args.output/'mobile.png'),full_page=True)
    page.get_by_role('button',name='Concluídas',exact=True).click()
    expect(page.locator('.consultations-card--finalizada')).to_have_count(1)
    verify('finalizada','rgb(121, 237, 77)')
    expect(page.locator('.consultations-summary .consultations-status-led')).to_have_count(0)
    page.locator('.consultations-card--finalizada .consultations-patient-button').click()
    verify_summary('rgb(121, 237, 77)')
    page.emulate_media(reduced_motion='reduce')
    track=page.locator('.consultations-card .consultations-status-led .vet-date-led-track')
    expect(track).to_have_css('animation-duration','12s')
    verify('finalizada','rgb(121, 237, 77)')
    verify_summary('rgb(121, 237, 77)')
    page.set_viewport_size({'width':1440,'height':1000})
    page.screenshot(path=str(args.output/'completed-green.png'))
    page.get_by_role('button',name='Canceladas',exact=True).click()
    expect(page.locator('.consultations-card--cancelada')).to_have_count(1)
    expect(page.locator('.consultations-status-led')).to_have_count(0)
    page.locator('.consultations-patient-button').first.click()
    expect(page.locator('.consultations-summary')).to_contain_text('Max')
    expect(page.locator('.consultations-summary .consultations-status-led')).to_have_count(0)
    assert not errors, errors
    browser.close()
print('OK: LEDs vermelho/amarelo/verde, sentido horário, halo móvel, cliques, temas, mobile e movimento reduzido.')
