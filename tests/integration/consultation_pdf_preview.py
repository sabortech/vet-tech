"""Copy into an isolated /tmp Reflex app; synthetic API, request counts, no real data."""
import os
import sys
import asyncio
sys.path.insert(0, os.environ['VET_TECH_SOURCE_ROOT'])
sys.path.insert(0, os.environ['VET_TECH_SOURCE_ROOT'] + '/tests/unit')
import reflex as rx
from test_consultation_pdf import export_payload
from vet_tech.features.auth.state import State
from vet_tech.components.consultation_pdf import consultation_pdf_dialog
from vet_tech.pages.profile import _records_header
from vet_tech.components.clinical import attendance_content
from vet_tech.components.veterinary_schedule import consultation_card, schedule_card
from vet_tech.shared.xano_client import XanoRequestError
import vet_tech.features.clinical.state as clinical

async def fake_request(method, group, path, **kwargs):
    await asyncio.sleep(.12)
    if kwargs.get('auth_token') == 'synthetic-audit-failure':
        raise XanoRequestError('Falha sintética', status_code=500)
    if kwargs.get('auth_token') == 'synthetic-revoked':
        raise XanoRequestError('Revogado', status_code=403)
    parts = path.split('/')
    result=export_payload(int(parts[-2]), int(parts[2]))
    result['consulta']['obs']='Observação sintética com ç ã é.\n' + ('Texto longo para conferir a rolagem. '*80)
    result['exames']=[{'id':1,'pet_id':7,'consulta_id':int(parts[-2]),'tipo':'Hemograma','resultado':'Resultado sintético'}]
    return result
clinical.xano_request=fake_request

class Preview(rx.State):
    view: str='tutor'
    @rx.event
    async def setup(self):
        state=await self.get_state(State)
        state._invalidate_pdf_export()
        state._auth_token='synthetic-only';state.is_authenticated=True;state.profile='tutor'
        state.selected_pet={'id':'7','nome':'Amora','foto':''};state.active_section='Consultas'
        state.history_rows={'consultas':[{'id':str(i),'status':'finalizada' if i!=44 else 'legado'} for i in (42,43,44)]}
        State.show_consultation_detail.fn(state,'42')
        state.clinical_id='42';state.clinical_pet_id='7';state.clinical_pet_name='Amora';state.clinical_status='finalizada'
        state.agenda_rows=[{'id':'42','pet_id':'7','status':'finalizada','autorizado':'sim',
            'pet_nome':'Amora','pet_foto':'','foto_ausente':'sim','quando':'04/11/2026','status_label':'Concluída','hora':'11:00','motivo':'Avaliação'}]
    @rx.event
    async def set_view(self, view: str):
        state=await self.get_state(State)
        state._invalidate_pdf_export()
        state.profile='tutor' if view=='tutor' else 'veterinario'
        state._auth_token='synthetic-only'
        state.vet_section='Consultas' if view=='agenda' else 'Horários'
        state.upcoming_rows=[dict(row) for row in state.agenda_rows]
        self.view=view
    @rx.event
    async def fail(self):
        state=await self.get_state(State);state._auth_token='synthetic-audit-failure'
    @rx.event
    async def revoke(self):
        state=await self.get_state(State);state._auth_token='synthetic-revoked'


def preview():
    return rx.box(
        rx.flex(*[rx.button(label,on_click=Preview.set_view(view)) for view,label in
                  [('tutor','Perfil tutor'),('attendance','Atendimento finalizado'),('agenda','Consulta reaberta'),('schedule','Agenda do dia')]],
                rx.button('Falha sintética',on_click=Preview.fail),
                rx.button('Revogar acesso',on_click=Preview.revoke),
                rx.button('Alternar tema',on_click=rx.toggle_color_mode()),gap='12px',wrap='wrap',margin_bottom='24px'),
        rx.cond(Preview.view=='tutor',rx.box(_records_header('Consultas','Consulta sintética'),consultation_pdf_dialog()),
            rx.cond(Preview.view=='attendance',attendance_content(),
                rx.box(rx.cond(Preview.view=='schedule',rx.foreach(State.agenda_rows,lambda row: schedule_card(row)),rx.foreach(State.upcoming_rows,consultation_card)),consultation_pdf_dialog()))),
        padding='24px',min_height='100vh')

app=rx.App(stylesheets=['/vet_tech.css'])
app.add_page(preview,route='/',on_load=Preview.setup)
