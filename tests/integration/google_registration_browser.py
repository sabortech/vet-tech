"""Verifica layout de cadastro em desktop/celular e ambos os temas."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import argparse
args=argparse.ArgumentParser(); args.add_argument('--output',type=Path,default=Path('/tmp/vet-tech-google-layout')); args=args.parse_args()
out=args.output;out.mkdir(parents=True,exist_ok=True)
checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless=True,args=['--no-sandbox'])
 for width in [390,1100]:
  for theme in ['light','dark']:
   page=browser.new_page(viewport={'width':width,'height':1100},color_scheme=theme)
   page.add_init_script('localStorage.setItem("vet_tech_theme", '+json.dumps(theme)+')'); page.goto('http://127.0.0.1:3000/cadastro');page.wait_for_selector('input[name=cpf]');page.wait_for_timeout(1500)
   assert page.locator('button[title="Cadastrar com Google"]').is_visible()
   boxes={k:page.locator(f'input[name={k}]').bounding_box() for k in ['nome','email','cpf','endereco','telefone']}
   gaps=[round(boxes[b]['y']-boxes[a]['y']-boxes[a]['height'],2) for a,b in [('nome','email'),('email','cpf'),('cpf','endereco'),('endereco','telefone')]]
   assert max(gaps)-min(gaps)<1,gaps
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
   page.screenshot(path=str(out/f'cadastro-{width}-{theme}.png'),full_page=True)
   page.locator('input[name=cpf]').fill('123');page.wait_for_timeout(500);assert page.get_by_text('CPF inválido.',exact=True).is_visible()
   checks.append({'width':width,'theme':theme,'gaps':gaps,'overflow':False,'cpf_feedback':True})
   page.close()
 browser.close()
(out/'layout.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
