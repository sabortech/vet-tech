"""Verificação com API sintética da escolha centralizada e temas da tela sem pet.

PYTHONPATH=/tmp/vet-tech-browser-tools .venv/bin/python tests/integration/pet_selection_browser.py
"""
import os,sys,json,socket,threading,subprocess,time,signal
from pathlib import Path
from http.server import ThreadingHTTPServer
import httpx
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/integration'))
import dashboard_dates_browser as fixture
OUT=ROOT/'openspec/changes/archive/2026-11-07-centralizar-selecao-pet/evidence';OUT.mkdir(exist_ok=True)
MULTI_RECORDS=False
PET_DETAILS_RELEASE=threading.Event()
PET_DETAILS_RELEASE.set()
class API(fixture.SyntheticAPI):
 def handle_api(self):
  from urllib.parse import urlsplit
  path=urlsplit(self.path).path.split('/',2)[-1]
  fixture.REQUESTS.append({'method':self.command,'path':path,'payload':{}})
  if self.command=='GET' and path in ('pets/1','pets/2'):
   PET_DETAILS_RELEASE.wait(timeout=45)
   body=dict(fixture.PET if path=='pets/1' else fixture.PET2)
   body.pop('foto',None)  # Published detail contract may omit the list photo.
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(body).encode())
  elif self.command=='GET' and path.endswith('/historico'):
   body={'vacinas': [{'vacina': 'Vacina de teste com nome longo para verificar quebra', 'data_aplicacao': '2026-10-12', 'lote': '12564', 'data_prox_dose': '2027-10-12', 'consulta_id': 42, 'veterinario_id': 8}], 'medicamentos': [{'nome': 'Vitamina D', 'dose': 0, 'unidade': 'mg', 'frequencia': 'Dia sim, dia não', 'via': 'Oral', 'tipo': 'Outro', 'data_inicio': '2026-11-02', 'data_fim': '2026-11-30', 'consulta_id': 43, 'veterinario_id': 8}], 'doencas': [], 'consultas': [], 'exames': []}
   for group in ('vacinas','medicamentos'):
    body[group][0]['id']='1'
    if MULTI_RECORDS:
     body[group]+=[{**body[group][0],'id':str(i)} for i in (2,3)]
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(body).encode())
  else:super().handle_api()
api=ThreadingHTTPServer(('127.0.0.1',0),API);threading.Thread(target=api.serve_forever,daemon=True).start()
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
env_file=ROOT/'.web/env.json';original=env_file.read_bytes()
env={**os.environ,'XANO_API_BASE_URL':f'http://127.0.0.1:{api.server_port}','XANO_TENANT':''}
log=(OUT/'reflex.log').open('w');proc=subprocess.Popen([str(ROOT/'.venv/bin/reflex'),'run','--env','prod','--single-port','--backend-port',str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
results=[]
try:
 origin=f'http://localhost:{port}'
 fixture.PET.update(foto=origin+'/mascote/clinicturtle.jpeg',sexo='Feminino',peso_atual=0,num_microchip=0)
 for _ in range(240):
  if proc.poll() is not None:raise RuntimeError('Server exited')
  try:
   if httpx.get(origin,timeout=1).status_code==200:break
  except httpx.HTTPError:pass
  time.sleep(.5)
 else:raise RuntimeError('Server timeout')
 env_file.write_bytes(original)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(15000)
  page.set_default_navigation_timeout(45000)
  optimized_responses=[]
  page.on('response',lambda response: optimized_responses.append({'url':response.url.split('/optimized/')[-1],'status':response.status}) if '/optimized/' in response.url else None)
  page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
  page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
  page.goto(origin+'/login',wait_until='domcontentloaded');page.get_by_label('E-mail',exact=True).fill('tutor@example.invalid');page.get_by_label('Senha',exact=True).fill('synthetic-password');page.get_by_role('button',name='Login',exact=True).click();expect(page.get_by_role('heading',name='Perfil do tutor')).to_be_visible()
  page.locator('.sidebar a[href="/dashboard"]').click()
  expect(page.locator('.dashboard-selected-pet')).to_have_count(0)
  page.locator('.sidebar a[href="/"]').click()
  expect(page.get_by_role('heading',name='Perfil do tutor')).to_be_visible()
  for section in ['inicio','vacinas','medicamentos','doencas','consultas']:
   page.goto(origin+'/prontuario?secao='+section);expect(page.locator('.pet-selection-empty')).to_be_visible();expect(page.locator('.pet-list')).to_have_count(0)
   results.append({'section':section,'empty':True})
  for width in [1440,768,390]:
   page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
   for theme in ['light','dark']:
    page.evaluate('(t)=>document.documentElement.setAttribute("data-vt-theme",t)',theme)
    page.locator('.pet-selection-empty').scroll_into_view_if_needed();page.wait_for_timeout(300)
    state=page.locator('.pet-selection-empty').evaluate('''async el=>{const bg=getComputedStyle(el.closest(".app-content")).backgroundImage;const im=new Image();im.src=bg.slice(5,-2);await im.decode();return {width:el.clientWidth,scroll:el.scrollWidth,bg}}''')
    led=page.locator('.pet-selection-led .vet-date-led-track')
    start=led.evaluate('(el)=>getComputedStyle(el).strokeDashoffset')
    page.wait_for_timeout(200)
    finish=led.evaluate('(el)=>getComputedStyle(el).strokeDashoffset')
    assert start!=finish, (start,finish)
    assert led.evaluate('(el)=>getComputedStyle(el).animationName')=='vet-date-border-orbit'
    assert page.locator('.pet-selection-art-frame').evaluate('(el)=>getComputedStyle(el).pointerEvents')=='none'
    assert state['scroll']<=state['width'],state
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/f'{width}-{theme}.png'),full_page=True);results.append({'width':width,'theme':theme,**state})
  page.get_by_role('button',name='Selecionar pet em Meus Pets').click();expect(page.get_by_role('heading',name='Perfil do tutor')).to_be_visible()
  PET_DETAILS_RELEASE.clear()
  page.locator('.pet-list').get_by_role('button',name='Abrir ',exact=False).first.click();page.wait_for_url('**/dashboard');expect(page.locator('.pet-selection-empty')).to_have_count(0)
  page.set_viewport_size({'width':1440,'height':1000})
  expect(page.locator('.dashboard-scope [role="combobox"]')).to_contain_text(fixture.PET['nome'])
  expect(page.locator('.dashboard-selected-pet')).to_have_count(0)
  page.locator('.dashboard-scope [role="combobox"]').click()
  page.get_by_role('option',name='Todos os pets',exact=True).click()
  expect(page.locator('.dashboard-selected-pet')).to_contain_text(fixture.PET['nome'])
  for width in [1440,390]:
   page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
   for theme in ['light','dark']:
    page.evaluate('(t)=>document.documentElement.setAttribute("data-vt-theme",t)',theme)
    indicator=page.locator('.dashboard-selected-pet').bounding_box()
    selected_card=page.locator('.dashboard-pet-card').filter(has=page.locator('.dashboard-selected-pet'))
    stamp=selected_card.locator('.dashboard-pet-stamp').bounding_box()
    name=selected_card.locator('.dashboard-pet-name').bounding_box()
    assert indicator['x']>=name['x'] and indicator['x']+indicator['width']<=stamp['x']+1,(indicator,name,stamp)
    assert abs(indicator['y']-name['y'])<=8,(indicator,name)
    assert page.locator('.dashboard-selected-pet').evaluate('(e)=>getComputedStyle(e).position')!='fixed'
    assert page.locator('.dashboard-selected-pet').evaluate('(e)=>getComputedStyle(e).borderTopLeftRadius')=='999px'
    assert page.locator('.dashboard-selected-pet').evaluate('(e)=>getComputedStyle(e).borderTopRightRadius')=='10px'
    page.screenshot(path=str(OUT/f'dashboard-selected-pet-{width}-{theme}.png'),full_page=False)
  page.locator('.dashboard-selected-pet').click()
  expect(page.locator('.dashboard-scope [role="combobox"]')).to_contain_text(fixture.PET['nome'])
  expect(page.locator('.dashboard-selected-pet')).to_have_count(0)
  page.set_viewport_size({'width':1440,'height':1000})
  PET_DETAILS_RELEASE.set()
  page.wait_for_timeout(250)
  assert not any(r['path'].endswith('/historico') or r['path']=='tutor/consultas' for r in fixture.REQUESTS),fixture.REQUESTS
  results.append({'dashboard_does_not_prefetch_history':True})
  results.append({'dashboard_general_identifies_selected_pet_during_details_load':True})

  page.locator('.sidebar a[href="/prontuario"]').click()
  expect(page.locator('#pet-details .rt-Heading')).to_be_visible()
  expect(page.locator('.pet-record-fact')).to_have_count(5)
  expect(page.get_by_role('button',name='Atualizar dados',exact=True)).to_be_enabled()
  assert sum(r['path'].endswith('/historico') for r in fixture.REQUESTS)==1
  results.append({'clinical_entry_loads_history_once':True})
  expect(page.locator('.pet-record-led')).to_have_count(7)
  track=page.locator('.pet-record-photo-led .vet-date-led-track')
  initial_offset=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
  page.wait_for_timeout(250)
  assert initial_offset!=track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
  expect(page.locator('.pet-record-photo img')).to_have_attribute('src',fixture.PET['foto'])
  for width in [1440,1024,390]:
   page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
   for theme in ['light','dark']:
    page.evaluate('(t)=>document.documentElement.setAttribute("data-vt-theme",t)',theme)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/f'prontuario-{width}-{theme}.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1000})
  page.locator('.sidebar a[href="/prontuario?secao=vacinas"]').click()
  expect(page.locator('.pet-selection-empty')).to_have_count(0)
  expect(page.locator('.vaccine-record-card')).to_have_count(1)
  expect(page.locator('.vaccine-record-card > .vaccine-record-led')).to_have_count(1)
  original_vaccine_background=page.locator('.vaccine-record-art').evaluate('(e)=>getComputedStyle(e).getPropertyValue("--record-background")')
  vaccine_track=page.locator('.vaccine-record-led .vet-date-led-track')
  vaccine_offset=vaccine_track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
  page.wait_for_timeout(250)
  assert vaccine_offset!=vaccine_track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
  for width in [1440,390]:
   page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
   for theme in ['light','dark']:
    page.evaluate('(t)=>document.documentElement.setAttribute("data-vt-theme",t)',theme)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(OUT/f'vacinas-{width}-{theme}.png'),full_page=True)
  page.locator('.vaccine-record-footer .rt-Button').click()
  expect(page.get_by_role('heading',name='Prontuário da consulta',exact=True)).to_be_visible()
  page.set_viewport_size({'width':1440,'height':1000})
  page.locator('.sidebar a[href="/prontuario?secao=medicamentos"]').click()
  expect(page.locator('.medication-card')).to_have_count(1)
  expect(page.locator('.medication-card')).to_contain_text('0 mg')
  for width in [1440,1024,390]:
   page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
   for theme in ['light','dark']:
    page.evaluate('(t)=>document.documentElement.setAttribute("data-vt-theme",t)',theme)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert page.locator('.medication-mascot').evaluate('(img)=>img.complete && img.naturalWidth>0')
    page.screenshot(path=str(OUT/f'medicamentos-{width}-{theme}.png'),full_page=True)
  original_medication_background=page.locator('.medication-art').evaluate('(e)=>getComputedStyle(e).getPropertyValue("--record-background")')
  MULTI_RECORDS=True
  page.set_viewport_size({'width':1440,'height':1000})
  page.get_by_role('button',name='Atualizar registros do pet',exact=True).click()
  expect(page.locator('.medication-card')).to_have_count(3)
  backgrounds=page.locator('.medication-art').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).getPropertyValue("--record-background"))')
  assert len(set(backgrounds))==3,backgrounds
  assert backgrounds[0]==original_medication_background
  assert len(set(page.locator('.medication-mascot').evaluate_all('(els)=>els.map(e=>e.src)')))==1
  page.screenshot(path=str(OUT/'medicamentos-multiple-backgrounds.png'),full_page=True)
  page.get_by_role('button',name='Atualizar registros do pet',exact=True).click()
  expect(page.locator('.medication-card')).to_have_count(3)
  page.wait_for_timeout(300)
  assert backgrounds==page.locator('.medication-art').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).getPropertyValue("--record-background"))')
  page.locator('.sidebar a[href="/prontuario?secao=vacinas"]').click()
  expect(page.locator('.vaccine-record-art')).to_have_count(3)
  vaccine_backgrounds=page.locator('.vaccine-record-art').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).getPropertyValue("--record-background"))')
  assert len(set(vaccine_backgrounds))==3,vaccine_backgrounds
  assert vaccine_backgrounds[0]==original_vaccine_background
  page.screenshot(path=str(OUT/'vacinas-multiple-backgrounds.png'),full_page=True)
  page.locator('.sidebar a[href="/prontuario?secao=medicamentos"]').click()
  results.append({'backgrounds_vary_per_record_and_remain_stable':True})
  page.locator('.medication-origin-button').first.click()
  expect(page.get_by_role('heading',name='Prontuário da consulta',exact=True)).to_be_visible()


  results.append({'select_and_navigate':True})
  page.set_viewport_size({'width':1440,'height':1000})
  page.locator('.sidebar a[href="/"]').click()
  selected=page.locator('.pet-entry__action[aria-pressed="true"]')
  expect(selected).to_have_count(1)
  expect(selected).to_have_text('Pet selecionado')
  for width in [1440,390]:
   page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
   for theme in ['light','dark']:
    page.evaluate('(t)=>document.documentElement.setAttribute("data-vt-theme",t)',theme)
    actions=page.locator('.pet-entry__action').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,width:r.width}})')
    assert max(a['x'] for a in actions)-min(a['x'] for a in actions)<1,actions
    assert max(a['width'] for a in actions)-min(a['width'] for a in actions)<1,actions
    page.locator('.pet-list').screenshot(path=str(OUT/f'pet-list-{width}-{theme}.png'))
  page.locator('.pet-entry__action[aria-pressed="false"]').first.click()
  page.wait_for_url('**/dashboard')
  expect(page.locator('.dashboard-scope [role="combobox"]')).to_contain_text(fixture.PET2['nome'])
  page.set_viewport_size({'width':1440,'height':1000})
  page.locator('.sidebar a[href="/"]').click()
  expect(page.locator('.pet-entry__action[aria-pressed="true"]')).to_have_count(1)
  results.append({'pet_list_aligned_and_selection_changes':True})
  assert optimized_responses and all(r['status']==200 for r in optimized_responses),optimized_responses
  results.append({'optimized_assets_loaded':optimized_responses})
  browser.close()
 (OUT/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
finally:
 env_file.write_bytes(original);os.killpg(proc.pid,signal.SIGINT)
 try:proc.wait(timeout=20)
 except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM)
 api.shutdown();log.close()
