"""Real settings UI checks using only existing synthetic development fixtures."""
import argparse
import json
from pathlib import Path
import sys
import time

import httpx
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from vet_tech.shared.config import get_xano_base_url
from vet_tech.shared.xano_client import AUTH_API_GROUP

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://localhost:3000')
parser.add_argument('--chromium',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
config=json.loads((ROOT/'.env.foundation-fixtures.json').read_text())
assert config['environment']=='development' and config['synthetic'] is True
assert config['origin'].rstrip('/')==get_xano_base_url()
credentials=config['identity_credentials']['vet_b']
assert credentials['email'].endswith('@example.invalid')
args.output.mkdir(parents=True,exist_ok=True)
results=[]

def note(text):
    results.append(text)
    print(json.dumps({'scenario':text,'status':'passed'},ensure_ascii=False),flush=True)
    (args.output/'browser-live.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')


def api_call(method,path,payload=None,token=None):
    time.sleep(3)
    r=api.request(method,'/api:'+AUTH_API_GROUP+'/'+path,json=payload,headers={'Authorization':'Bearer '+token} if token else {})
    assert r.status_code==200,f'{method} {path}: HTTP {r.status_code}'
    return r.json()


with httpx.Client(base_url=config['origin'],timeout=35) as api, sync_playwright() as p:
    token=api_call('POST','acesso/login',credentials)['authToken']
    original=api_call('GET','veterinario/account',token=token)
    browser=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000})
    page=context.new_page()
    page.set_default_timeout(35000)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    saved=False
    try:
        page.goto(args.url+'/login')
        page.locator('[name="email"]').fill(credentials['email'])
        page.locator('[name="password"]').fill(credentials['password'])
        page.get_by_role('button',name='Login',exact=True).click()
        page.get_by_role('heading',name='Horários',exact=True).wait_for()
        page.wait_for_timeout(3500)
        page.locator('.sidebar-navigation').get_by_role('link',name='Configurações',exact=True).click()
        page.get_by_text('Perfil: Veterinário',exact=True).wait_for()
        page.wait_for_function("document.querySelector('#settings-nome')?.value === "+json.dumps(original['nome']))
        assert page.locator('.sidebar-navigation .sidebar-item').all_text_contents()==['Horários','Consultas','Configurações']
        assert page.locator('.sidebar-item--active').inner_text()=='Configurações'
        assert not page.locator('#settings-email').is_editable()
        assert not page.locator('#settings-crmv').is_editable()
        assert page.locator('#settings-cpf,#settings-endereco').count()==0
        page.screenshot(path=str(args.output/'account-desktop.png'),full_page=True)
        note('Veterinário: menu correto e conta real carregada com CRMV/e-mail bloqueados e sem CPF/endereço')
        page.locator('#settings-nome').fill('Fixture rascunho descartado')
        page.get_by_role('button',name='Cancelar',exact=True).click()
        page.wait_for_function("document.querySelector('#settings-nome')?.value === "+json.dumps(original['nome']))
        page.locator('#settings-nome').fill('Fixture navegador configurações médicas')
        page.wait_for_timeout(3000)
        page.get_by_role('button',name='Salvar alterações',exact=True).click()
        page.get_by_text('Dados atualizados com sucesso.',exact=True).wait_for()
        saved=True
        page.locator('#settings-nome').fill(original['nome'])
        page.get_by_text('Dados atualizados com sucesso.',exact=True).wait_for(state='hidden')
        page.wait_for_timeout(3000)
        page.get_by_role('button',name='Salvar alterações',exact=True).click()
        page.get_by_text('Dados atualizados com sucesso.',exact=True).wait_for()
        saved=False
        note('Cancelar e salvar confirmados no backend; nome da fixture restaurado')
        page.locator('#settings-nome').fill('Fixture edição pendente')
        page.locator('.sidebar-navigation').get_by_role('link',name='Consultas',exact=True).click()
        page.get_by_role('alertdialog').wait_for()
        page.get_by_role('button',name='Continuar editando',exact=True).click()
        page.get_by_role('alertdialog').wait_for(state='hidden')
        assert page.locator('#settings-nome').input_value()=='Fixture edição pendente'
        page.locator('.sidebar-navigation').get_by_role('link',name='Consultas',exact=True).click()
        page.get_by_role('button',name='Descartar alterações',exact=True).click()
        page.get_by_role('heading',name='Consultas',exact=True).wait_for()
        assert 'secao=consultas' in page.url
        page.wait_for_timeout(3000)
        page.locator('.sidebar-navigation').get_by_role('link',name='Configurações',exact=True).click()
        page.get_by_text('Perfil: Veterinário',exact=True).wait_for()
        page.locator('#settings-nome').wait_for()
        page.wait_for_timeout(600)
        page.get_by_role('tab',name='Segurança',exact=True).click()
        page.wait_for_function("document.querySelector('#tab-security')?.getAttribute('aria-selected')==='true'")
        page.locator('#current_password').fill('incorrect-synthetic-password')
        page.locator('#new_password').fill('synthetic-not-saved')
        page.locator('#password_confirmation').fill('synthetic-not-saved')
        page.wait_for_timeout(3000)
        page.get_by_role('button',name='Atualizar senha',exact=True).click()
        page.get_by_text('Senha atual incorreta.',exact=True).wait_for()
        page.get_by_role('tab',name='Preferências',exact=True).click()
        page.locator('#theme-switch').check()
        page.wait_for_function("document.documentElement.dataset.vtTheme==='dark'")
        page.locator('#sidebar-switch').click()
        page.locator('.sidebar--collapsed').wait_for()
        page.locator('#sidebar-switch').click()
        page.locator('.sidebar--collapsed').wait_for(state='detached')
        page.get_by_role('tab',name='Segurança',exact=True).click()
        page.locator('#current_password').wait_for()
        assert page.locator('#current_password').input_value()==''
        page.screenshot(path=str(args.output/'security-dark-desktop.png'),full_page=True)
        note('Descarte preserva destino Consultas; senha inválida não encerra sessão; limpeza e preferências funcionam')
        page.set_viewport_size({'width':390,'height':844})
        page.get_by_role('tab',name='Preferências',exact=True).click()
        page.wait_for_timeout(400)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(args.output/'preferences-dark-mobile.png'),full_page=True)
        page.get_by_role('button',name='Abrir menu',exact=True).filter(visible=True).click()
        page.locator('.sidebar--mobile-open').wait_for()
        page.screenshot(path=str(args.output/'menu-dark-mobile.png'))
        page.locator('.sidebar-navigation').get_by_role('link',name='Horários',exact=True).click()
        page.get_by_role('heading',name='Horários',exact=True).wait_for()
        assert 'secao=horarios' in page.url
        page.locator('.sidebar--mobile-open').wait_for(state='detached')
        note('Celular: tema escuro, drawer, retorno para Horários e ausência de overflow')
        # Separate browser context proves tutor fields/menu remain isolated.
        tutor_context=browser.new_context(viewport={'width':1440,'height':1000})
        tutor=tutor_context.new_page()
        tutor.set_default_timeout(35000)
        tutor.goto(args.url+'/login')
        tutor.locator('[name="email"]').fill(config['identity_credentials']['tutor_a']['email'])
        tutor.locator('[name="password"]').fill(config['identity_credentials']['tutor_a']['password'])
        tutor.get_by_role('button',name='Login',exact=True).click()
        tutor.get_by_role('link',name='Configurações',exact=True).wait_for()
        tutor.wait_for_timeout(7000)
        tutor.get_by_role('link',name='Configurações',exact=True).click()
        tutor.get_by_text('Perfil: Tutor',exact=True).wait_for()
        tutor.locator('#settings-cpf').wait_for()
        assert not tutor.locator('#settings-cpf').is_editable()
        assert tutor.locator('#settings-endereco').count()==1
        assert tutor.locator('#settings-crmv').count()==0
        assert tutor.locator('.sidebar-navigation').get_by_text('Meus Pets',exact=True).count()==1
        tutor.screenshot(path=str(args.output/'tutor-regression.png'),full_page=True)
        assert not errors,errors
        note('Tutor mantém campos e menu anteriores; nenhuma exceção JavaScript')
        tutor_context.close()
    except Exception:
        page.screenshot(path=str(args.output/'failure-debug.png'),full_page=True)
        raise
    finally:
        if saved:
            restored=api_call('PATCH','veterinario/account',{'nome':original['nome'],'telefone':original['telefone']},token)
            assert restored==original
        browser.close()
