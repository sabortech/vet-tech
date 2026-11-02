"""Copy to an isolated /tmp Reflex preview; never load in the real app."""
import asyncio
from datetime import datetime, timezone
import os
import sys
sys.path.insert(0, os.environ['VET_TECH_SOURCE_ROOT'])
import reflex as rx
import vet_tech.features.clinical.state as clinical
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import attendance_content, veterinary_content

_record = {'status': 'em_atendimento', 'versao': 1}
_history_attempts = {}
_scheduled = int(datetime(2026, 11, 3, 13, tzinfo=timezone.utc).timestamp()*1000)

async def fake_request(method, group, path, **kwargs):
    await asyncio.sleep(.15)
    if method == 'PUT' and path.endswith('/rascunho'):
        _record['versao'] += 1
        return dict(_record)
    if method == 'POST' and path.endswith('/finalizar'):
        _record['status'] = 'finalizada'
        _record['versao'] += 1
        return dict(_record)
    if path.endswith('/historico'):
        pet_id = path.split('/')[-2]
        _history_attempts[pet_id] = _history_attempts.get(pet_id, 0) + 1
        if pet_id == '2' and _history_attempts[pet_id] == 1:
            raise ValueError('Falha sintética ao consultar o pet do card')
        name = 'Nina' if pet_id == '2' else 'Jessy'
        return {'pet':{'nome':name, 'sexo':'Feminino', 'data_nasc':'2026-01-31', 'peso_atual':10},
                'historico':{'consultas':[{'data_atendimento':'2026-10-01','diagnostico':'Avaliação anterior de '+name,'obs':'Em acompanhamento'}],
                             'vacinas':[{'vacina':'Vacina sintética','data_aplicacao':'2026-10-01'}], 'medicamentos':[], 'doencas':[], 'exames':[]}}
    if path.startswith('veterinario/agenda?'):
        common = {'agendada_para': _scheduled, 'autorizado': True, 'pet_id': 1, 'motivo': 'Consulta de rotina'}
        items = [dict(common, id=43, pet_nome='Jessy', status=_record['status'], pet_foto=os.environ.get('VET_TECH_PREVIEW_URL', 'http://localhost:3027')+'/mascote_logo.png'),
                 dict(common, id=44, pet_id=2, pet_nome='Pet sem foto', status='em_atendimento'),
                 {'id':45, 'status':'agendada', 'agendada_para':_scheduled, 'autorizado':False}]
        if 'dia=' not in path:
            items = [row for row in items if row['status'] != 'finalizada']
        return {'items': items, 'total': len(items)}
    raise AssertionError(f'Unexpected synthetic request: {method} {path}')

clinical.xano_request = fake_request

class Preview(rx.State):
    @rx.event
    async def setup(self):
        _record.update(status='em_atendimento', versao=1)
        _history_attempts.clear()
        state = await self.get_state(State)
        state._auth_token = 'synthetic-preview-only'
        state.profile = 'veterinario'
        state.is_authenticated = True
        state.clinical_id = '43'
        state.clinical_pet_id = '1'
        state.clinical_pet_name = 'Jessy'
        state.clinical_pet_info = {'nome':'Jessy', 'sexo':'Feminino', 'nascimento':'31/01/2026', 'peso':'10'}
        state.clinical_status = state.router.url.query_parameters.get('status', 'em_atendimento')
        state.clinical_version = 1
        state.clinical_agenda_day = '2026-11-03'
        state.clinical_date = '2026-11-02'
        state.clinical_reason = 'Consulta de rotina'
        state.clinical_diagnosis = 'Avaliação sintética'
        state.vet_section = 'Consultas'
        state.agenda_day = '2026-11-02'
        state.clinical_dirty = False
        state.clinical_lines = {group: [] for group in clinical.GROUPS}

app = rx.App(
    stylesheets=['https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap', '/vet_tech.css'],
    head_components=[rx.el.script(src='/preferences.js')],
    toaster=rx.toast.provider(position='bottom-left', offset='24px'),
)
app.add_page(attendance_content, route='/atendimento/[consulta_id]', on_load=Preview.setup)
app.add_page(lambda: rx.box(veterinary_content(), class_name='vet-schedule', padding='24px',
                           on_mount=State.enter_veterinary_agenda), route='/')
