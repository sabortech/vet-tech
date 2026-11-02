"""Observe complete LED loops in real time, including reduced-motion preference."""
import argparse
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:3015')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1100,'height':900})
    page=context.new_page()
    served=page.request.get('http://localhost:3000/vet_tech.css').text()
    assert 'vet-date-border-orbit 6s linear infinite' in served
    assert '.vet-date-led-track { animation-duration: 12s; }' in served
    for width,height in [(1100,900),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto(args.url)
        page.locator('.vet-schedule-card').first.wait_for()
        for preference,duration in [('no-preference',6),('reduce',12)]:
            page.emulate_media(reduced_motion=preference)
            page.get_by_role('button',name='Escolher data',exact=True).click()
            track=page.locator('.vet-date-led-track');track.wait_for()
            settings=track.evaluate('(e)=>({duration:getComputedStyle(e).animationDuration,easing:getComputedStyle(e).animationTimingFunction,iterations:getComputedStyle(e).animationIterationCount,state:getComputedStyle(e).animationPlayState,dash:getComputedStyle(e).strokeDasharray})')
            assert settings['duration']==f'{duration}s' and settings['easing']=='linear'
            assert settings['iterations']=='infinite' and settings['state']=='running'
            assert settings['dash']!='none'
            values=[]
            # Do not pause, seek, or change playback time: test actual continuous motion.
            for i in range(math.ceil((duration+.7)/.25)):
                values.append(float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px','')))
                if i in (0, math.ceil(duration/.5)):
                    page.screenshot(path=str(args.output/f'{width}-{preference}-{i}.png'))
                page.wait_for_timeout(250)
            steps=[(a-b)%100 for a,b in zip(values,values[1:])]
            assert all(0<step<15 for step in steps),steps
            assert any(b>a for a,b in zip(values,values[1:])), 'A complete loop must wrap without stopping'
            assert page.get_by_role('dialog').evaluate('(e)=>e.scrollWidth<=e.clientWidth+2')
            results.append({'width':width,'preference':preference,'duration':duration,'frames':len(values),'clockwise':True,'continuous_loop':True})
            print(json.dumps(results[-1]),flush=True)
            (args.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
            page.keyboard.press('Escape')
            track.wait_for(state='hidden')
            page.locator('.rt-DialogOverlay').wait_for(state='detached')
    context.close()
    browser.close()
(args.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
