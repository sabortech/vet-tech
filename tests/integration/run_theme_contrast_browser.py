"""Verificação visual de contraste e sincronização do tema, sem login real."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://localhost:3000')
parser.add_argument('--chromium', required=True)
parser.add_argument('--output', type=Path, default=Path('/tmp/vet-tech-contrast-evidence'))
args = parser.parse_args()
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
def lum(c):
    values=[int(c[i:i+2],16)/255 for i in (1,3,5)]
    return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip([.2126,.7152,.0722],values))
def contrast(a,b):
    a,b=sorted([lum(a),lum(b)]);return round((b+.05)/(a+.05),2)
pairs=[('texto','#182b21','#ffffff'),('secundário','#4e5d55','#ffffff'),('placeholder','#4e5d55','#eef0f2'),('primário','#ffffff','#477b36'),('link','#35632b','#ffffff'),('sidebar','#ffffff','#477b36')]
for n,a,b in pairs: assert contrast(a,b)>=4.5,(n,contrast(a,b))
results={'contraste':{n:contrast(a,b) for n,a,b in pairs},'navegador':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=args.chromium)
    page=browser.new_page(viewport={'width':1366,'height':900},color_scheme='dark')
    errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
    page.add_init_script("localStorage.setItem('vet_tech_theme','light');localStorage.setItem('theme','dark');")
    for route in ['/login','/cadastro']:
        page.goto(args.url.rstrip('/')+route);page.wait_for_timeout(1600)
        assert page.locator('html').get_attribute('data-vt-theme')=='light'
        assert page.locator('.radix-themes.dark').count()==0
        page.screenshot(path=str(OUT/(route[1:]+'-claro.png')),full_page=True)
        results['navegador'].append(route+': tema claro com preferência Reflex escura; sem contêineres escuros')
    page.evaluate('''() => {
      const host=document.createElement('div'); host.id='contrast-fixture';
      host.className='radix-themes dark';host.dataset.accentColor='grass';
      host.style='position:fixed;inset:20px;z-index:99999;overflow:auto;background:var(--vt-surface);padding:32px';
      host.innerHTML=`<h1 class="rt-Heading">Componentes compartilhados — tutor e veterinário</h1>
        <p id="sample-body" class="rt-Text">Prontuário, consultas, vacinas, medicamentos, doenças e exames</p>
        <p id="sample-muted" class="rt-Text" style="color:var(--gray-11)">Informações complementares</p>
        <div class="rt-TextFieldRoot"><input id="sample-input" class="rt-TextFieldInput" value="Nome do pet"></div>
        <textarea class="rt-TextAreaInput" placeholder="Observações clínicas"></textarea>
        <table class="rt-TableRoot"><tbody><tr><td class="rt-TableCell">Consulta agendada</td></tr></tbody></table>
        <button id="sample-button" class="rt-Button rt-variant-solid" style="background:var(--accent-9);color:var(--accent-contrast)">Salvar</button>
        <a id="sample-link" style="color:var(--accent-11)">Ver histórico</a>
        <p class="settings-hint">Texto auxiliar de configurações</p>
        <div class="settings-control"><input class="settings-input" readonly value="Dado somente leitura"></div>
        <div class="rt-SelectContent"><div class="rt-SelectItem">Opção do menu</div></div>
        <div class="rt-DialogContent"><h2 class="rt-DialogTitle">Agendar consulta</h2><p class="rt-DialogDescription">Escolha dia e horário</p></div>
        <label>Modo escuro <input id="test-theme" type="checkbox" data-vt-preference="theme"></label>`;
      document.body.append(host);
    }''')
    page.wait_for_timeout(250)
    assert 'light' in page.locator('#contrast-fixture').get_attribute('class')
    def color(s):return page.locator(s).evaluate('(e)=>getComputedStyle(e).color')
    assert color('#sample-body')=='rgb(24, 43, 33)',color('#sample-body')
    assert color('#sample-muted')=='rgb(78, 93, 85)',color('#sample-muted')
    assert color('#sample-link')=='rgb(53, 99, 43)',color('#sample-link')
    page.screenshot(path=str(OUT/'componentes-claro.png'))
    page.locator('#test-theme').check();page.wait_for_timeout(200)
    assert page.locator('html').get_attribute('data-vt-theme')=='dark'
    assert page.locator('.radix-themes.light').count()==0
    assert color('#sample-body')=='rgb(238, 243, 239)',color('#sample-body')
    page.screenshot(path=str(OUT/'componentes-escuro.png'))
    page.locator('#test-theme').uncheck();page.wait_for_timeout(200)
    assert color('#sample-body')=='rgb(24, 43, 33)'
    results['navegador'].append('Componentes representativos, portal dinâmico, claro → escuro → claro: passou')
    assert not errors,errors
    browser.close()
print(json.dumps(results,ensure_ascii=False,indent=2))
(OUT/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
