"""Check the chat's continuous figure-eight SVG on an isolated synthetic preview."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:3027/atendimento/43')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
args.output.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(args.url)
    page.get_by_role('heading',name='Jessy',exact=True).wait_for()
    page.add_style_tag(path=str(root/'assets/vet_tech.css'))
    page.add_style_tag(path=str(root/'assets/support-chat.css'))
    page.add_script_tag(path=str(root/'assets/support-chat.js'))
    page.evaluate("window.dispatchEvent(new CustomEvent('vettech:mascote-click'))")
    chat=page.locator('.vt-chat[open]');expect(chat).to_be_visible()
    track=chat.locator('path.vt-chat-led-track')
    expect(track).to_have_attribute('pathLength','100')
    def geometry():
        return chat.evaluate('''e=>{const p=e.querySelector('.vt-chat-led-track'),b=e.querySelector('.vt-chat-banner');
          const split=b.offsetTop+b.offsetHeight,total=p.getTotalLength();let divider=0,upper=0,lower=0,invalid=0;
          for(let i=0;i<500;i++){const q=p.getPointAtLength(total*i/500);
            if(Math.abs(q.y-split)<1 && q.x>25 && q.x<e.clientWidth-25)divider++;
            else if(q.y<split)upper++;else lower++;
            if(q.x<0||q.y<0||q.x>e.clientWidth||q.y>e.clientHeight)invalid++;
          }return {split,total,divider,upper,lower,invalid,d:p.getAttribute('d'),width:e.clientWidth,height:e.clientHeight}}''')
    previous=None
    for width,height in [(1440,1000),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        page.wait_for_timeout(250)
        data=geometry()
        assert data['divider']>20 and data['upper']>50 and data['lower']>50,data
        assert data['invalid']==0,data
        if previous:assert data['d']!=previous
        previous=data['d']
        for theme in ['light','dark']:
            page.evaluate("theme=>window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:theme}))",theme)
            start=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
            page.wait_for_timeout(150)
            assert track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')!=start
            assert track.evaluate('(e)=>getComputedStyle(e).filter').count('drop-shadow')==3
            # Seek only the screenshot to show the light crossing the banner divider.
            track.evaluate('(e)=>{const a=e.getAnimations()[0];a.currentTime=0;a.pause()}')
            page.screenshot(path=str(args.output/f'{width}-{theme}-divider.png'))
            track.evaluate('(e)=>e.getAnimations()[0].play()')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        results.append({k:v for k,v in data.items() if k!='d'})
    page.emulate_media(reduced_motion='reduce')
    assert track.evaluate('(e)=>getComputedStyle(e).animationDuration')=='12s'
    assert chat.locator('.vt-chat-led').evaluate('(e)=>getComputedStyle(e).pointerEvents')=='none'
    # A change to the actual banner height also updates the route.
    before=geometry()['split']
    chat.locator('.vt-chat-banner-video').evaluate('(e)=>e.style.aspectRatio="2 / 1"')
    page.wait_for_timeout(250)
    assert geometry()['split']!=before
    assert geometry()['divider']>20
    chat.get_by_role('button',name='Fechar chat',exact=True).click()
    page.locator('.vt-chat[open]').wait_for(state='hidden')
    assert page.locator('.vt-chat path.vt-chat-led-track').evaluate('(e)=>e.getAnimations().length')==0
    assert not errors,errors
    browser.close()
(args.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS: duas voltas, divisória real, movimento, temas, resize e fechamento')
