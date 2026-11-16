"""Revisa prévias locais de boas-vindas; sem cadastro ou envio de e-mail."""
import argparse
import json
from PIL import Image
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--chromium',default='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome');p.add_argument('--output',type=Path,default=ROOT/'openspec/changes/archive/2026-11-16-enviar-boas-vindas-cadastro/evidence/email');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox'])
        for profile in ('tutor','veterinario'):
            for width in (390,900):
                page=browser.new_page(viewport={'width':width,'height':1000},device_scale_factor=1)
                page.goto((a.output/(profile+'.html')).as_uri());page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                assert page.locator('h1').inner_text()=='Que bom ter você no Vet Tech!'
                assert page.locator('img').count()==5
                img=page.locator('img[alt^="Tartaruga Vet Tech cuidando"]');ratio=img.evaluate('(i)=>(i.width/i.height)/(i.naturalWidth/i.naturalHeight)');assert abs(ratio-1)<0.02
                assert 'Copyright © by Vet Tech Team' in page.locator('body').inner_text()
                assert page.get_by_role('link',name='Acesse nosso sistema',exact=True).get_attribute('href')=='http://localhost:3000/login'
                assert page.locator('a').count()==1
                assert page.locator('table[background]').count()==1
                mascot=page.locator('img[alt*="braços em V"]');assert mascot.is_visible()
                assert mascot.bounding_box()['x']<page.get_by_text('Vet Tech',exact=True).first.bounding_box()['x']
                header=page.locator('td[bgcolor]').first.bounding_box();box=mascot.bounding_box()
                asset=Image.open(ROOT/'assets/consultation-pdf/mascote-v-clean.png')
                opaque_bottom=asset.getchannel('A').point(lambda a:255 if a>=250 else 0).getbbox()[3]
                visible_bottom=box['y']+box['height']*opaque_bottom/asset.height
                assert abs(visible_bottom-(header['y']+header['height']))<0.3
                assert box['width']>=100
                page.screenshot(path=str(a.output/(profile+'-'+str(width)+'.png')),full_page=True)
                checks.append({'profile':profile,'width':width,'overflow':False,'all_images_loaded':True,'clinic_proportion_preserved':True})
                page.evaluate('document.querySelectorAll("img").forEach(i=>{i.removeAttribute("src");i.style.height="32px"})')
                assert 'Seus próximos passos' in page.locator('body').inner_text()
                page.screenshot(path=str(a.output/(profile+'-'+str(width)+'-no-images.png')),full_page=True)
                page.close()
        browser.close()
    (a.output/'visual-results.json').write_text(json.dumps({'checks':checks,'email_sent':False},indent=2));print('PASS: 4 prévias responsivas e conteúdo essencial sem imagens.')

if __name__=='__main__':main()
