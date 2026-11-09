"""Validate the actual SVG animation in led_preview.py, not just its CSS class."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright, expect

out=Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1280,'height':900})
 errors=[];page.on('pageerror',lambda error: errors.append(str(error)))
 page.goto('http://localhost:3041')
 results=[]
 for width in (1280,390):
  page.set_viewport_size({'width':width,'height':900})
  for theme in ('light','dark'):
   page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark");document.documentElement.classList.toggle("light",t==="light");document.querySelectorAll(".radix-themes").forEach(e=>{e.classList.toggle("dark",t==="dark");e.classList.toggle("light",t==="light")})}',theme)
   for reduced in ('no-preference','reduce'):
    page.emulate_media(reduced_motion=reduced)
    for value,color in [('1','rgb(255, 82, 82)'),('2','rgb(250, 204, 21)'),('3','rgb(121, 237, 77)')]:
     card=page.locator(f'[data-appointment-id="{value}"]')
     led=card.locator(':scope > .vet-schedule-card-led')
     expect(led).to_have_count(1)
     track=led.locator('rect')
     values=track.evaluate('(e)=>{const s=getComputedStyle(e);return {color:s.stroke,filter:s.filter,duration:s.animationDuration,name:s.animationName,pointer:s.pointerEvents,offset:parseFloat(s.strokeDashoffset)}}')
     assert values['color']==color,(value,values)
     assert values['duration']==('20s' if reduced=='reduce' else '8s'),values
     assert values['pointer']=='none' and values['name']=='vet-date-border-orbit'
     assert color in values['filter']
     page.wait_for_timeout(400)
     later=track.evaluate('(e)=>parseFloat(getComputedStyle(e).strokeDashoffset)')
     delta=(values['offset']-later+100)%100
     assert .5<delta<15,delta
     a=card.bounding_box();b=led.bounding_box()
     assert abs(a['width']-b['width'])<3 and abs(a['height']-b['height'])<3,(a,b)
     results.append({'width':width,'theme':theme,'motion':reduced,'status':value,'color':values['color'],'duration':values['duration'],'clockwise_delta':delta,'passed':True})
    for value in ('4','5'):
     expect(page.locator(f'[data-appointment-id="{value}"] > .vet-schedule-card-led')).to_have_count(0)
    page.screenshot(path=str(out/f'led-{width}-{theme}-{reduced}.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 # A longer card still has the LED on its full border, and it does not eat clicks.
 card=page.locator('[data-appointment-id="3"]')
 card.locator('.vet-schedule-reason').evaluate('(e)=>e.textContent="Conteúdo extenso de teste. ".repeat(20)')
 a=card.bounding_box();b=card.locator(':scope > .vet-schedule-card-led').bounding_box()
 assert abs(a['height']-b['height'])<3
 button=card.get_by_role('button',name='Histórico',exact=True)
 button.scroll_into_view_if_needed();button.click()
 expect(page.get_by_role('dialog',name='Histórico anterior',exact=True)).to_be_visible()
 assert not errors,errors
 (out/'results.json').write_text(json.dumps({'animation_cases':results,'neutral_states_without_led':True,'dynamic_height':True,'history_click':True,'javascript_errors':errors},ensure_ascii=False,indent=2)+'\n')
 browser.close()
print('OK: LED gira no cartão nas três cores; temas, celular, movimento reduzido, altura e cliques preservados.')
