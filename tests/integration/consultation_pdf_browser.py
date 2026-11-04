"""Synthetic preview download and regression check; never run against real data."""
import argparse
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from playwright.sync_api import sync_playwright,expect
parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://localhost:3041');parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
 context=browser.new_context(accept_downloads=True,viewport={'width':1280,'height':900})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(args.url)
 button=page.get_by_role('button',name='Exportar PDF da consulta',exact=True);expect(button).to_be_visible()
 with page.expect_download() as result:button.click()
 download=result.value;assert download.suggested_filename=='vettech-consulta-42.pdf'
 path=args.output/'consulta-sintetica-42.pdf';download.save_as(path)
 data=path.read_bytes();assert data.startswith(b'%PDF-')
 text=''.join(p.extract_text() for p in PdfReader(BytesIO(data)).pages)
 assert 'Amora' in text and 'Avaliação' in text and 'LUNA' not in text
 expect(page.get_by_text('PDF pronto para download.',exact=True)).to_be_visible()
 assert page.url.rstrip('/')==args.url.rstrip('/')
 page.screenshot(path=str(args.output/'desktop.png'))
 page.get_by_role('button',name='Consulta 44',exact=True).click();expect(button).to_have_count(0)
 page.get_by_role('button',name='Consulta 43',exact=True).click();expect(button).to_be_visible()
 other=browser.new_context(accept_downloads=True).new_page();other.goto(args.url)
 with other.expect_download() as d2, page.expect_download() as d1:
  other.get_by_role('button',name='Exportar PDF da consulta',exact=True).click()
  button.click()
 assert d1.value.suggested_filename=='vettech-consulta-43.pdf' and d2.value.suggested_filename=='vettech-consulta-42.pdf'
 downloads=[];page.on('download',lambda d:downloads.append(d))
 button.click();page.get_by_role('button',name='Consulta 42',exact=True).click();page.wait_for_timeout(1000)
 assert not downloads
 page.get_by_role('button',name='Falha sintética',exact=True).click();button.click()
 expect(page.get_by_text('Não foi possível exportar o PDF. Tente novamente.',exact=True)).to_be_visible()
 assert not downloads
 page.get_by_role('button',name='Consulta 42',exact=True).evaluate('(e)=>e.parentElement.style.flexWrap="wrap"')
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(args.output/'mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 assert not errors,errors
 browser.close()
print('OK: download dinâmico, dados corretos, duas sessões, legado, contexto atrasado, falha de auditoria, desktop/celular.')
