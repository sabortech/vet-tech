"""Check shared active-link/button styling across authenticated profile navigation."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:3000')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
fixture=json.loads((ROOT/'.env.foundation-fixtures.json').read_text())
assert fixture['environment']=='development' and fixture['synthetic'] is True
results=[]


def check(page,label):
    active=page.locator('.sidebar-navigation .sidebar-item--active')
    page.wait_for_function('(label)=>document.querySelectorAll(".sidebar-navigation .sidebar-item--active").length===1 && document.querySelector(".sidebar-navigation .sidebar-item--active").getAttribute("aria-label")===label',arg=label)
    page.mouse.move(1000,30)
    active.evaluate('(e)=>e.blur()')
    page.wait_for_timeout(220)
    colors=active.evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,text:getComputedStyle(e).color,icon:getComputedStyle(e.querySelector("svg")).color})')
    assert colors=={'bg':'rgb(255, 255, 255)','text':'rgb(26, 54, 41)','icon':'rgb(26, 54, 41)'},(label,colors)
    active.hover();page.wait_for_timeout(200)
    assert active.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(235, 238, 229)'
    page.keyboard.press('Tab');active.focus()
    assert active.evaluate('(e)=>getComputedStyle(e).color')=='rgb(26, 54, 41)'
    results.append(label+': ativo/hover/foco legíveis')


with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
    errors=[]
    for role in ('veterinario','tutor'):
        context=browser.new_context(viewport={'width':1440,'height':1000})
        context.add_init_script("localStorage.setItem('vet_tech_theme','dark')")
        page=context.new_page();page.set_default_timeout(35000)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(args.url+'/login')
        credential=fixture['identity_credentials']['vet_b' if role=='veterinario' else 'tutor_a']
        assert credential['email'].endswith('@example.invalid')
        page.locator('[name=email]').fill(credential['email']);page.locator('[name=password]').fill(credential['password'])
        page.get_by_role('button',name='Login',exact=True).click()
        page.locator('.sidebar-navigation').wait_for()
        if role=='veterinario':
            check(page,'Horários')
            page.locator('.sidebar-navigation').get_by_role('button',name='Consultas',exact=True).click();check(page,'Consultas')
        else:
            page.wait_for_timeout(7000)
            check(page,'Meus Pets')
            for name in ('Prontuário','Vacinas','Consultas'):
                page.locator('.sidebar-navigation').get_by_role('link',name=name,exact=True).click();check(page,name)
        page.locator('.sidebar-navigation').get_by_role('link',name='Configurações',exact=True).click();check(page,'Configurações')
        page.mouse.move(1000,30)
        page.screenshot(path=str(args.output/(role+'-dark-desktop.png')))
        page.evaluate("dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'light'}))")
        check(page,'Configurações')
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate("dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'dark'}))")
        page.get_by_role('button',name='Abrir menu',exact=True).filter(visible=True).click()
        page.locator('.sidebar--mobile-open').wait_for()
        page.wait_for_timeout(300)
        active=page.locator('.sidebar-navigation .sidebar-item--active')
        assert active.evaluate('(e)=>getComputedStyle(e).backgroundColor') in ('rgb(255, 255, 255)','rgb(235, 238, 229)')
        page.screenshot(path=str(args.output/(role+'-dark-mobile.png')))
        context.close()
        print(role+': navegação e destaque consistentes nos temas claro/escuro e no drawer',flush=True)
    assert not errors,errors
    browser.close()
(args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
