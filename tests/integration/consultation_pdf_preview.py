"""Copy into an isolated /tmp Reflex app; no real APIs or clinical data."""
import os
import sys
import asyncio
sys.path.insert(0,os.environ['VET_TECH_SOURCE_ROOT'])
sys.path.insert(0,os.environ['VET_TECH_SOURCE_ROOT']+'/tests/unit')
import reflex as rx
from test_consultation_pdf import export_payload
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import consultation_detail
from vet_tech.shared.xano_client import XanoRequestError
import vet_tech.features.clinical.state as clinical

async def fake_request(method,group,path,**kwargs):
    await asyncio.sleep(.3)
    if kwargs.get('auth_token')=='synthetic-audit-failure':
        raise XanoRequestError('Não foi possível concluir a solicitação.',status_code=500)
    parts=path.split('/')
    return export_payload(int(parts[-2]),int(parts[2]))
clinical.xano_request=fake_request
class Preview(rx.State):
    @rx.event
    async def setup(self):
        state=await self.get_state(State)
        state._auth_token='synthetic-only';state.is_authenticated=True;state.profile='tutor'
        state.selected_pet={'id':'7'};state.active_section='Consultas'
        state.history_rows={'consultas':[{'id':str(i),'status':'finalizada' if i!=44 else 'legado','motivo':'Avaliação sintética','diagnostico':'Registro de exemplo','obs':'Sem dados reais','veterinario_id':'3'} for i in (42,43,44)]}
        State.show_consultation_detail.fn(state,'42')
    @rx.event
    async def fail(self):
        state=await self.get_state(State)
        state._auth_token='synthetic-audit-failure'
    @rx.event
    async def clear_pet(self):
        state=await self.get_state(State)
        state._clear_pet_context()

def preview():
    return rx.vstack(rx.hstack(*[rx.button(f'Consulta {i}',on_click=State.show_consultation_detail(str(i))) for i in (42,43,44)],
                              rx.button('Falha sintética',on_click=Preview.fail),rx.button('Limpar pet',on_click=Preview.clear_pet),wrap='wrap'),
                     consultation_detail(),padding='24px',align='stretch')
app=rx.App(stylesheets=['/vet_tech.css'])
app.add_page(preview,route='/',on_load=Preview.setup)
