"""Isolated synthetic preview; never load this module in the real application."""
import os,sys,asyncio
sys.path.insert(0,os.environ['VET_TECH_SOURCE_ROOT'])
import reflex as rx
import vet_tech.features.auth.state as auth_module
import vet_tech.features.clinical.state as clinical_module
from vet_tech.features.auth.state import State
from vet_tech.pages.profile import veterinarian_area
from vet_tech.shared.xano_client import XanoRequestError
_mode='normal';_attempts=0
async def fake_request(method,group,path,**kwargs):
    global _attempts
    await asyncio.sleep(.15)
    if path=='veterinario/account':
        _attempts+=1
        if _mode=='failure' and _attempts==1:raise XanoRequestError('Falha sintética',status_code=500)
        return {'crmv':'' if _mode=='missing' else '12345','crmv_uf':'' if _mode=='missing' else 'SP'}
    if path.startswith('veterinario/agenda?'):return {'items':[],'total':0,'contrato_consultas':2}
    raise AssertionError('Unexpected synthetic request: '+path)
auth_module.xano_request=fake_request
clinical_module.xano_request=fake_request
class Preview(rx.State):
    @rx.event
    async def setup(self):
        global _mode,_attempts
        state=await self.get_state(State)
        _mode=self.router.url.query_parameters.get('scenario','normal');_attempts=0
        state._session_generation+=1
        state.profile='veterinario';state._auth_token='synthetic-only';state.identity_id='7'
        state.identity_name='Dra. Fernanda Diniz' if _mode!='long' else 'Dra. Fernanda Albuquerque de Vasconcelos Diniz'
        state.is_authenticated=True
        state.identity_crmv=state.identity_crmv_uf=''
        state.identity_professional_loaded=state.identity_professional_loading=state.identity_professional_error=False
        yield State.load_professional_identity
app=rx.App(stylesheets=['/vet_tech.css'],head_components=[rx.el.script(src='/preferences.js')])
app.add_page(veterinarian_area,route='/',on_load=Preview.setup)
