"""Copy into an isolated /tmp Reflex app; uses synthetic data only."""
import os
import sys
sys.path.insert(0, os.environ["VET_TECH_SOURCE_ROOT"])
import reflex as rx
from urllib.parse import urlparse,parse_qs
from vet_tech.features.auth.state import State
import vet_tech.features.clinical.state as clinical
import vet_tech.features.auth.state as auth_module
from vet_tech.pages.profile import veterinarian_area

async def fake_request(method,group,path,**kwargs):
    if path == 'veterinario/account':
        return {'crmv':'12345','crmv_uf':'SP'}
    import asyncio
    await asyncio.sleep(.1)
    if path.endswith('/historico'):
        pet=path.split('/')[-2]
        return {'pet':{'nome':'Max' if pet=='1' else 'Mel', 'data_nasc':'2023-05-20','peso_atual':16 if pet=='1' else 4},'historico':{
            'doencas':[{'nome':'Alergia alimentar','estado':'controlada'}] if pet=='1' else [],
            'consultas':[{'data_atendimento':'2026-10-21','motivo':'Rotina'}],
            'vacinas':[{'vacina':'Antirrábica','data_aplicacao':'2026-09-01'}]}}
    params=parse_qs(urlparse(path).query)
    rows=[{'id':i,'pet_id':1 if i==1 else 2,'pet_nome':'Max' if i==1 else 'Mel','pet_foto':os.environ.get('VET_TECH_PREVIEW_PHOTO','') if i==1 else '',
           'status':'agendada' if i==1 else 'em_atendimento','autorizado':True,'agendada_para':1793703600000,'motivo':'Vacinação anual' if i==1 else 'Retorno pós-operatório'} for i in range(1,6)]
    if params.get('aba')==['Concluídas']: rows=[dict(rows[0],status='finalizada')] if os.environ.get('VET_TECH_PREVIEW_LED') == '1' else []
    if params.get('aba')==['Canceladas']: rows=[dict(rows[0],status='cancelada')]
    if params.get('busca'): rows=[r for r in rows if params['busca'][0].casefold() in r['pet_nome'].casefold()]
    return {'items':rows,'total':len(rows),'contrato_consultas':2}
clinical.xano_request=fake_request
auth_module.xano_request=fake_request
class Preview(rx.State):
    @rx.event
    async def setup(self):
        state=await self.get_state(State)
        state._auth_token='synthetic-only';state.profile='veterinario';state.is_authenticated=True
        state.identity_name='Dra. Fernanda Diniz';state.vet_section='Consultas'
        async for event in state.load_agenda():
            yield event
app=rx.App(stylesheets=['/vet_tech.css'],head_components=[rx.el.script(src='/preferences.js')])
app.add_page(veterinarian_area,route='/',on_load=Preview.setup)
