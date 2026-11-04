from pathlib import Path
import json
from playwright.sync_api import sync_playwright, expect
root=Path('/home/usuario/vet-tech')
out=root/'openspec/changes/enquadrar-foto-horarios/evidence'
out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1100})
 page.goto('http://localhost:3038')
 frame=page.locator('[data-appointment-id="1"] .vet-schedule-avatar-frame')
 expect(frame.locator('img')).to_be_visible()
 results=[]
 for viewport in [{'width':1440,'height':1100},{'width':390,'height':844}]:
  page.set_viewport_size(viewport)
  for theme in ['light','dark']:
   page.evaluate('(t)=>window.dispatchEvent(new StorageEvent("storage",{key:"vet_tech_theme",newValue:t}))',theme)
   for w,h in [(200,100),(100,200),(100,100)]:
    src='data:image/svg+xml,'+__import__('urllib.parse',fromlist=['quote']).quote(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="green"/><circle cx="{w/2}" cy="{h/2}" r="30" fill="gold"/></svg>')
    frame.locator('img').evaluate('(e,s)=>e.src=s',src)
    dims=frame.evaluate('''e=>{let r=e.getBoundingClientRect();return {frame:[r.width,r.height],layers:[...e.querySelectorAll('div[role="img"],.consultations-avatar,.rt-AvatarRoot,img')].map(n=>{let r=n.getBoundingClientRect(),s=getComputedStyle(n);return {w:r.width,h:r.height,fit:s.objectFit,pos:s.objectPosition}}),overflow:getComputedStyle(e).overflow}}''')
    assert dims['frame']==[52,52],dims
    assert all(x['w']==50 and x['h']==50 for x in dims['layers']),dims
    assert dims['layers'][-1]['fit']=='cover',dims
    assert dims['overflow']=='visible',dims
    results.append({'viewport':viewport,'theme':theme,'photo':[w,h],**dims})
   track=frame.locator('.vet-date-led-track')
   page.screenshot(path=str(out/f"{viewport['width']}-{theme}-0.png"),full_page=True)
   start=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
   page.wait_for_timeout(250)
   end=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
   assert start!=end
   assert frame.locator('svg.vet-date-led').evaluate('(e)=>getComputedStyle(e).pointerEvents')=='none'
   page.screenshot(path=str(out/f"{viewport['width']}-{theme}-1.png"),full_page=True)
   page.emulate_media(reduced_motion='reduce')
   expect(track).to_have_css('animation-duration','16s')
   reduced=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset');page.wait_for_timeout(150)
   assert track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')!=reduced
   page.emulate_media(reduced_motion='no-preference')
 # Shared avatar styles are identical with and without the schedule rules.
 page.evaluate('''()=>{let e=document.createElement('div');e.className='consultations-summary';e.innerHTML='<div class="consultations-avatar"><span class="rt-AvatarRoot rt-r-size-5"><img class="rt-AvatarImage" src="/mascote02.png" /></span></div>';document.body.append(e)}''')
 baseline=page.locator('.consultations-summary').last.evaluate('(e)=>[...e.querySelectorAll("*")].map(n=>{let s=getComputedStyle(n);return [s.width,s.height,s.borderRadius,s.objectFit]})')
 css=(root/'assets/vet_tech.css').read_text()
 import re
 stripped=re.sub(r'[^{}]*\.vet-schedule-avatar-frame[^{}]*\{[^{}]*\}', '',css)
 page.add_style_tag(content=stripped)
 assert baseline==page.locator('.consultations-summary').last.evaluate('(e)=>[...e.querySelectorAll("*")].map(n=>{let s=getComputedStyle(n);return [s.width,s.height,s.borderRadius,s.objectFit]})')
 for card_id,label in [('1','Começar consulta'),('2','Retomar')]:
  page.goto('http://localhost:3038')
  button=page.locator(f'[data-appointment-id="{card_id}"]').get_by_role('button',name=label,exact=True)
  expect(button).to_be_enabled();button.click();page.wait_for_url(f'**/atendimento/{card_id}')
 (out/'geometry-results.json').write_text(json.dumps(results,indent=2))
 b.close()
print('OK: 12 combinações de geometria, LED móvel, movimento reduzido, estilos compartilhados e iniciar/retomar com backend sintético.')
