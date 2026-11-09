"""Browser checks for status_preview.py served in an isolated Reflex app."""
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
 for value,status,visible in [('1','agendada',False),('2','em_atendimento',False),('3','finalizada',True),('4','cancelada',False),('5','desconhecida',False),('6','finalizada sem autorização',False)]:
  card=page.locator(f'[data-consultation-id="{value}"]')
  expect(card).to_be_visible()
  button=card.get_by_role('button',name='Ver Histórico anterior',exact=True)
  if visible:expect(button).to_be_visible()
  else:expect(button).to_have_count(0)
  results.append({'status':status,'ver_prontuario':visible,'passed':True})
 expect(page.locator('[data-consultation-id="1"]').get_by_role('button',name='Iniciar atendimento',exact=True)).to_be_visible()
 expect(page.locator('[data-consultation-id="2"]').get_by_role('button',name='Retomar atendimento',exact=True)).to_be_visible()
 geometry=[]
 for width in (1280,1100,768,390):
  page.set_viewport_size({'width':width,'height':900})
  card=page.locator('[data-consultation-id="3"]')
  history=card.get_by_role('button',name='Ver Histórico anterior',exact=True)
  export=card.get_by_role('button',name='Exportar PDF da consulta',exact=True)
  a=history.bounding_box();b=export.bounding_box()
  assert abs(a['width']-b['width'])<1 and abs(a['height']-b['height'])<1,(a,b)
  assert history.evaluate('(el)=>getComputedStyle(el).whiteSpace')=='nowrap'
  assert history.evaluate('(el)=>el.scrollWidth<=el.clientWidth')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  geometry.append({'viewport':width,'width':a['width'],'height':a['height'],'equal_size':True,'single_line':True})
  page.screenshot(path=str(out/f'buttons-{width}.png'),full_page=True)
 assert not errors, errors
 page.screenshot(path=str(out/'status-matrix.png'),full_page=True)
 (out/'results.json').write_text(json.dumps({'cases':results,'start_resume_preserved':True,'geometry':geometry,'javascript_errors':errors},ensure_ascii=False,indent=2)+'\n')
 browser.close()
print('OK: Ver Histórico anterior somente na finalizada autorizada; iniciar/retomar preservados.')
