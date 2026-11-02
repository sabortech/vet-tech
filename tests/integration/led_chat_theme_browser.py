"""Visual preferences against real pages; chat transport is simulated, no AI calls."""
import argparse
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
from n8n_chat_browser import MOCK

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:3000')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
config=json.loads((ROOT/'.env.foundation-fixtures.json').read_text())
assert config['environment']=='development' and config['synthetic'] is True
results=[]


def note(value):
    results.append(value)
    print(value,flush=True)
    (args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')


def palette(page):
    for selector,prop,token in [('.vt-chat','backgroundColor','--vt-page-bg'),('.vt-chat','color','--vt-text'),
            ('.vt-chat-footer','backgroundColor','--vt-surface'),('.vt-chat-bubble','backgroundColor','--vt-surface'),
            ('.vt-chat-form input','backgroundColor','--vt-field-bg'),('.vt-chat-header','backgroundColor','--vt-green'),
            ('.vt-chat-header','color','--vt-primary-text')]:
        actual=page.locator(selector).first.evaluate('(e,p)=>getComputedStyle(e)[p]',prop)
        raw=page.evaluate('(t)=>getComputedStyle(document.documentElement).getPropertyValue(t).trim()',token)
        raw=raw.lstrip('#')
        if len(raw)==3:raw=''.join(c*2 for c in raw)
        expected='rgb('+', '.join(str(int(raw[i:i+2],16)) for i in (0,2,4))+')'
        assert actual==expected,(selector,prop,actual,expected)


def chat_check(page,tag):
    page.locator('#vettech-mascote').click()
    chat=page.locator('.vt-chat');chat.wait_for()
    palette(page)
    track=chat.locator('.vt-chat-led-track')
    assert track.get_attribute('pathLength')=='100'
    assert track.evaluate('(e)=>getComputedStyle(e).animationDuration')=='6s'
    assert chat.locator('.vt-chat-led').evaluate('(e)=>getComputedStyle(e).pointerEvents')=='none'
    before=float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px',''))
    page.wait_for_timeout(300)
    after=float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px',''))
    assert 0<(before-after)%100<25
    page.emulate_media(reduced_motion='reduce')
    assert track.evaluate('(e)=>getComputedStyle(e).animationDuration')=='12s'
    before=float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px',''))
    page.wait_for_timeout(300)
    after=float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px',''))
    assert 0<(before-after)%100<25
    page.emulate_media(reduced_motion='no-preference')
    question=page.get_by_role('textbox',name='Digite sua pergunta')
    question.fill('Pergunta genérica de teste')
    page.get_by_role('button',name='Enviar mensagem',exact=True).click()
    page.get_by_text('Resposta de teste: Pergunta genérica de teste',exact=True).wait_for()
    previous=page.locator('.vt-chat-messages').inner_text()
    page.evaluate("dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'light'}))")
    palette(page)
    assert page.locator('.vt-chat-messages').inner_text()==previous
    page.screenshot(path=str(args.output/(tag+'-chat-light.png')))
    page.evaluate("dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'dark'}))")
    palette(page)
    page.screenshot(path=str(args.output/(tag+'-chat-dark.png')))
    page.get_by_role('button',name='Fechar chat',exact=True).click()
    assert track.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
    page.locator('#vettech-mascote').click()
    page.get_by_role('button',name='Histórico de conversas',exact=True).click()
    page.locator('.vt-chat-history-entry').first.wait_for()
    raw=page.locator('.vt-chat-history-entry').first.evaluate('(e)=>getComputedStyle(e).backgroundColor')
    assert raw=='rgb(32, 38, 34)',raw
    page.screenshot(path=str(args.output/(tag+'-history-dark.png')))
    page.get_by_role('button',name='Fechar chat',exact=True).click()
    note(tag+': LED horário contínuo normal/reduzido, fechar/reabrir, temas e conversa/histórico passaram')


with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
    errors=[]
    for role in ('visitante','veterinario','tutor'):
        context=browser.new_context(viewport={'width':1440,'height':1000})
        context.add_init_script('('+MOCK+')();')
        if role=='visitante':context.add_init_script("localStorage.setItem('vet_tech_theme','dark')")
        page=context.new_page();page.set_default_timeout(35000)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(args.url+'/login')
        if role!='visitante':
            credential=config['identity_credentials']['vet_b' if role=='veterinario' else 'tutor_a']
            assert credential['email'].endswith('@example.invalid')
            page.locator('[name=email]').fill(credential['email'])
            page.locator('[name=password]').fill(credential['password'])
            page.get_by_role('button',name='Login',exact=True).click()
            page.locator('.sidebar-navigation').get_by_role('link',name='Configurações',exact=True).wait_for()
            if role=='veterinario':
                page.get_by_role('button',name='Escolher data',exact=True).click()
                dialog=page.locator('.vet-date-dialog');dialog.wait_for()
                track=dialog.locator('.vet-date-led-track')
                assert track.get_attribute('pathLength')=='100'
                assert track.evaluate('(e)=>e.getTotalLength()')>1000
                before=float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px',''))
                page.wait_for_timeout(300)
                after=float(track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset').replace('px',''))
                assert 0<(before-after)%100<25
                assert page.locator('.vet-date-calendar-button').evaluate('(e)=>getComputedStyle(e).animationName')=='none'
                for quarter in range(4):
                    track.evaluate('(e,t)=>{const a=e.getAnimations()[0];a.pause();a.currentTime=t}',quarter*1500)
                    page.screenshot(path=str(args.output/f'led-quarter-{quarter}.png'))
                track.evaluate('(e)=>e.getAnimations()[0].play()')
                assert dialog.locator('.vet-date-led').evaluate('(e)=>getComputedStyle(e).pointerEvents')=='none'
                page.emulate_media(reduced_motion='reduce')
                assert track.evaluate('(e)=>getComputedStyle(e).animationName')=='vet-date-border-orbit'
                assert track.evaluate('(e)=>getComputedStyle(e).animationDuration')=='12s'
                page.emulate_media(reduced_motion='no-preference')
                page.keyboard.press('Escape');dialog.wait_for(state='hidden')
                note('Calendário real: traço percorre perímetro horário, quatro fases capturadas, somente janela e movimento reduzido preservados')
            page.wait_for_timeout(4000)
            page.locator('.sidebar-navigation').get_by_role('link',name='Configurações',exact=True).click()
            page.get_by_text('Perfil: '+('Veterinário' if role=='veterinario' else 'Tutor'),exact=True).wait_for()
            page.wait_for_timeout(500)
            page.get_by_role('tab',name='Preferências',exact=True).click()
            page.locator('#theme-switch').check()
            page.wait_for_function("document.documentElement.dataset.vtTheme==='dark'")
        chat_check(page,role)
        if role=='visitante':
            page.goto(args.url+'/cadastro')
            page.locator('#vettech-mascote').click();page.locator('.vt-chat').wait_for();palette(page)
            page.get_by_role('button',name='Fechar chat',exact=True).click()
            page.set_viewport_size({'width':390,'height':844})
            page.locator('#vettech-mascote').click();page.locator('.vt-chat').wait_for();palette(page)
            page.wait_for_timeout(250)
            assert page.locator('.vt-chat').bounding_box()=={'x':0,'y':0,'width':390,'height':844}
            assert page.locator('.vt-chat').evaluate('(e)=>e.scrollWidth<=e.clientWidth+2')
            assert page.locator('.vt-chat-led-track').evaluate('(e)=>getComputedStyle(e).rx')=='0px'
            assert page.locator('.vt-chat-led-track').evaluate('(e)=>getComputedStyle(e).animationName')=='vt-chat-border-orbit'
            page.screenshot(path=str(args.output/'mobile-chat-dark.png'))
            note('Cadastro e celular: chat herda tema escuro e preserva layout fullscreen')
        context.close()
    assert not errors,errors
    browser.close()
