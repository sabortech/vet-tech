"""Isolated preview app; copy into a temporary Reflex project, never the real app."""
import sys
from datetime import datetime
import os
sys.path.insert(0, os.environ['VET_TECH_SOURCE_ROOT'])
import reflex as rx
from vet_tech.features.auth.state import State
from vet_tech.pages.profile import veterinarian_area
from vet_tech.components.sidebar import layout_com_menu
import vet_tech.features.clinical.state as clinical

async def fake_request(method, group, path, **kwargs):
    if '/historico' in path:
        return {'pet': {'nome': 'Pet sintético'}, 'historico': {'consultas': []}}
    day = path.split('dia=')[-1].split('&')[0] if 'dia=' in path else '2030-01-11'
    if day.endswith('-12'):
        return {'items': [], 'total': 0}
    if day.endswith('-13'):
        from vet_tech.shared.xano_client import XanoRequestError
        raise XanoRequestError('Falha simulada ao carregar agenda.', status_code=500)
    if 'page=2' in path:
        return {'items': [], 'total': 26}
    photo = 'https://images.unsplash.com/photo-1552053831-71594a27632d?w=100&h=100&fit=crop'
    return {'items': [dict(id=i,pet_id=5,pet_nome=name,motivo=reason,status=status,autorizado=allowed,
                          pet_foto=photo if i==1 else 'https://example.invalid/missing.jpg' if i==2 else '',
                          agendada_para=int(datetime.fromisoformat(day+'T'+time+':00-03:00').timestamp()*1000))
        for i, (name,time,reason,status,allowed) in enumerate([
            ('Max', '08:30', 'Consulta de rotina', 'agendada', True),
            ('Luna', '10:15', 'Vacinação', 'em_atendimento', True),
            ('Milo', '10:45', 'Retorno', 'finalizada', True),
            ('Nina', '13:00', 'Avaliação clínica', 'agendada', True),
            ('Privado', '15:00', 'Não deve aparecer', 'agendada', False),
            ('Nome longo para verificar o comportamento responsivo do cartão', '19:30', 'Acompanhamento de rotina com informações adicionais do agendamento', 'agendada', True),
        ],1)], 'total': 26}
clinical.xano_request = fake_request
class Preview(rx.State):
    @rx.event
    async def setup(self):
        state = await self.get_state(State)
        state.profile = 'veterinario'
        state.is_authenticated = True
        state._auth_token = 'synthetic-only'
        state.identity_name = 'Dra. Fernanda Diniz'
        state.agenda_day = '2030-01-11'
        state.vet_section = 'Horários'
        async for event in State.load_agenda.fn(state):
            if event is not None:
                yield event
app=rx.App(stylesheets=['/vet_tech.css'], head_components=[rx.el.script(src='/preferences.js')])
app.add_page(veterinarian_area, route='/', on_load=Preview.setup)
app.add_page(lambda: layout_com_menu(rx.heading('Menu padrão do tutor'), 'meus_pets'), route='/tutor')
