"""Synthetic shared-panel/browser verification; never target real clinical data."""
import argparse
from io import BytesIO
import json
from pathlib import Path
from pypdf import PdfReader
from playwright.sync_api import sync_playwright,expect
parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://localhost:3041');parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
 context=browser.new_context(accept_downloads=True,viewport={'width':1280,'height':900})
 page=context.new_page();errors=[];downloads=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('download',lambda d:downloads.append(d))
 page.goto(args.url)
 button=page.get_by_role('button',name='Exportar PDF da consulta',exact=True)
 panel=page.get_by_role('dialog',name='Tudo pronto para conferir')
 confirm=page.get_by_role('button',name='Baixar PDF da consulta',exact=True)
 for profile in ('Perfil tutor','Atendimento finalizado','Consulta reaberta','Agenda do dia'):
  page.get_by_role('button',name=profile,exact=True).click()
  expect(button).to_be_visible();button.click()
  expect(panel).to_be_visible();expect(page.locator('#consultation-pdf-pages figure').first).to_be_visible()
  expect(page.locator('#consultation-pdf-pages figure').first).to_have_attribute('data-rendered','true')
  expect(confirm).to_be_enabled()
  before=len(downloads)
  assert page.locator('.pdf-preview-mascot').is_visible()
  # Opening and dismissing the preview must never download.
  page.keyboard.press('Escape');expect(panel).not_to_be_visible()
  assert page.locator('#consultation-pdf-pages canvas').count()==0
  assert len(downloads)==before
  expect(button).to_be_focused()
  button.click();expect(confirm).to_be_enabled()
  with page.expect_download() as result:confirm.click()
  download=result.value;assert download.suggested_filename=='vettech-consulta-42.pdf'
  filename=profile.replace(' ','-').lower()
  path=args.output/(filename+'.pdf');download.save_as(path)
  data=path.read_bytes();assert data.startswith(b'%PDF-')
  text=''.join(pg.extract_text() for pg in PdfReader(BytesIO(data)).pages)
  assert 'Amora' in text and 'Hemograma' in text and 'LUNA' not in text
  expect(panel.get_by_text('PDF pronto para download.',exact=True)).to_be_visible()
  for size,width,height in [('desktop',1280,900),('mobile',390,844)]:
   page.set_viewport_size({'width':width,'height':height})
   for theme in ('light','dark'):
    page.evaluate('(theme)=>{document.documentElement.dataset.vtTheme=theme;document.documentElement.classList.toggle("dark",theme==="dark");document.documentElement.classList.toggle("light",theme==="light");document.querySelectorAll(".radix-themes").forEach(e=>{e.classList.toggle("dark",theme==="dark");e.classList.toggle("light",theme==="light")})}',theme)
    page.locator('#consultation-pdf-pages').evaluate('(e)=>e.scrollTop=0')
    expect(page.locator('#consultation-pdf-pages figure').first).to_have_attribute('data-rendered','true')
    page.screenshot(path=str(args.output/(filename+'-'+size+'-'+theme+'.png')))
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    bounds=panel.bounding_box();assert bounds and bounds['x']>=0 and bounds['x']+bounds['width']<=width+1
    viewer=page.locator('#consultation-pdf-pages')
    count=viewer.locator('figure').count();assert count>=2
    viewer.evaluate('(e)=>e.scrollTop=e.scrollHeight')
    expect(viewer.locator('figure').last).to_have_attribute('data-rendered','true')
    page.screenshot(path=str(args.output/(filename+'-'+size+'-'+theme+'-last-page.png')))
    # Every page remains available by scrolling; only nearby canvases occupy memory.
    assert viewer.locator('figure[data-rendered="true"]').count()<=4
    confirm.scroll_into_view_if_needed();expect(confirm).to_be_visible()
  page.get_by_role('button',name='Voltar',exact=True).click();expect(panel).not_to_be_visible()
  page.set_viewport_size({'width':1280,'height':900})
 # An audited export failure keeps the panel and provides safe feedback.
 page.get_by_role('button',name='Perfil tutor',exact=True).click();button.click();expect(confirm).to_be_enabled()
 page.keyboard.press('Escape')
 page.get_by_role('button',name='Falha sintética',exact=True).click();button.click()
 expect(panel.get_by_text('Não foi possível exportar o PDF. Tente novamente.',exact=True)).to_be_visible()
 expect(confirm).to_be_disabled()
 page.keyboard.press('Escape')
 assert not errors,errors
 (args.output/'results.json').write_text(json.dumps({'origins':4,'downloads':len(downloads),'themes':['light','dark'],'widths':[1280,390],'javascript_errors':errors},ensure_ascii=False,indent=2)+'\n')
 browser.close()
print('OK: quatro acessos, prévia sem download, cancelamento/foco, confirmação, PDF completo, temas e celular.')
