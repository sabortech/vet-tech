"""Copy into an isolated Reflex preview. Synthetic patients; no real requests."""
import os,sys,asyncio
sys.path.insert(0,os.environ['VET_TECH_SOURCE_ROOT'])
import reflex as rx
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import attendance_content
from vet_tech.shared.xano_client import XanoRequestError
import vet_tech.features.clinical.state as clinical
_mode='normal';_attempts=0
async def fake_request(method,group,path,**kwargs):
    global _attempts
    assert path.endswith('/historico'),path
    _attempts+=1
    await asyncio.sleep(.2)
    if _mode=='error' and _attempts==1:raise XanoRequestError('Falha sintética ao consultar histórico',status_code=500)
    groups={key:[] for key in ('consultas','vacinas','medicamentos','doencas','exames')}
    if _mode!='empty':
        groups['consultas']=[{'data_atendimento':'2026-10-01','diagnostico':'Avaliação anterior','obs':'Em acompanhamento'}]
        groups['vacinas']=[{'vacina':'Antirrábica','data_aplicacao':'2026-09-01'}]
    photo=os.environ.get('VET_TECH_PREVIEW_PHOTO','')
    if _mode=='no-photo':photo=''
    if _mode=='broken':photo='http://localhost:3038/missing-photo.png'
    return {'pet':{'nome':'Jessy','sexo':'Feminino','data_nasc':'2026-01-31','peso_atual':10,'foto':photo},'historico':groups}
clinical.xano_request=fake_request
class Preview(rx.State):
    @rx.event
    async def setup(self):
        global _mode,_attempts
        _mode=self.router.url.query_parameters.get('scenario','normal');_attempts=0
        state=await self.get_state(State)
        state._session_generation+=1
        state.profile='veterinario';state._auth_token='synthetic-only';state.is_authenticated=True
        state.clinical_id='43';state.clinical_pet_id='1';state.clinical_pet_name='Jessy';state.clinical_status='em_atendimento'
        state.clinical_date='2026-11-02';state.clinical_reason='Rotina';state.clinical_diagnosis='Rascunho preservado'
        state.clinical_lines={key:[] for key in ('vacinas','medicamentos','doencas','exames')}
        state.clinical_dirty=False
        state.prior_history={};state.prior_pet_info={};state.prior_history_message=''
app=rx.App(stylesheets=['/vet_tech.css'],head_components=[rx.el.script(src='/preferences.js')])
app.add_page(attendance_content,route='/',on_load=Preview.setup)
