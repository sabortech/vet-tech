from pathlib import Path
import json
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
root=Path('/home/usuario/vet-tech');out=root/'openspec/changes/enquadrar-foto-horarios/evidence'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1100})
 page.goto('http://localhost:3038')
 # Serve the current source stylesheet over the production preview's cached copy.
 page.add_style_tag(content=(root/'assets/vet_tech.css').read_text())
 page.locator('[data-appointment-id="1"]').get_by_role('button',name='Histórico',exact=True).click()
 portrait=page.locator('.history-profile-portrait');expect(portrait).to_be_visible()
 results=[]
 for width,height,size in [(1440,1100,120),(390,844,110)]:
  page.set_viewport_size({'width':width,'height':height})
  for theme in ['light','dark']:
   page.evaluate('(t)=>window.dispatchEvent(new StorageEvent("storage",{key:"vet_tech_theme",newValue:t}))',theme)
   for w,h in [(200,100),(100,200),(100,100)]:
    src='data:image/svg+xml,'+quote(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="green"/><circle cx="{w/2}" cy="{h/2}" r="30" fill="gold"/></svg>')
    portrait.locator('img').evaluate('(e,s)=>e.src=s',src)
    dims=portrait.evaluate('''e=>({frame:[e.offsetWidth,e.offsetHeight],layers:[...e.querySelectorAll('.consultations-avatar,.rt-AvatarRoot,img')].map(n=>({w:n.offsetWidth,h:n.offsetHeight,fit:getComputedStyle(n).objectFit}))})''')
    assert dims['frame']==[size,size],dims
    assert all(x['w']==size-4 and x['h']==size-4 for x in dims['layers']),dims
    assert dims['layers'][-1]['fit']=='cover'
    results.append({'viewport':width,'theme':theme,'photo':[w,h],**dims})
   expect(page.get_by_role('heading',name='Consultas',exact=True)).to_be_visible()
   for label in ['Vacinas','Medicamentos','Doenças','Exames']:
    expect(page.get_by_role('heading',name=label,exact=True)).to_have_count(1)
   page.screenshot(path=str(out/f'history-{width}-{theme}.png'))
 # Image failure keeps the existing error indicator; no placeholder is drawn over a loaded photo.
 expect(portrait.locator('.consultations-avatar-paw')).to_be_hidden()
 portrait.locator('img').evaluate('(e)=>e.remove()')
 expect(portrait.locator('[aria-label="Foto indisponível"]')).to_be_visible()
 page.get_by_role('button',name='Fechar histórico',exact=True).click()
 expect(page.locator('.attendance-history-dialog')).not_to_be_visible()
 track=page.locator('[data-appointment-id="1"] .vet-schedule-avatar-led .vet-date-led-track')
 first=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset');page.wait_for_timeout(150)
 assert track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')!=first
 (out/'history-geometry-results.json').write_text(json.dumps(results,indent=2))
 b.close()
print('OK: histórico preenchido em 12 combinações; categorias, fechar, indicador de erro e LED de Horários preservados.')
