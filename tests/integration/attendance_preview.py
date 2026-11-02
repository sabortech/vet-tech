"""Prévia isolada: copiar para preview/preview.py em /tmp; nunca importar no app real."""
import os
import sys
sys.path.insert(0,os.environ["VET_TECH_SOURCE_ROOT"])
import reflex as rx
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import attendance_content
from vet_tech.components.mascote_flutuante import mascote_app_wrap
class Preview(rx.State):
    @rx.event
    async def setup(self):
        state = await self.get_state(State)
        state.profile = "veterinario"
        state.is_authenticated = True
        state.clinical_id = "1"
        state.clinical_pet_id = "1"
        state.clinical_pet_name = "Jessy"
        state.clinical_pet_info = {"nome":"Jessy", "sexo":"Feminino", "nascimento":"31/01/2026", "peso":"10"}
        state.clinical_status = "em_atendimento"
        state.clinical_date = "2026-11-02"
        state.clinical_reason = "Consulta de rotina"
app=rx.App(extra_app_wraps={(6,"VetTechMascote"):mascote_app_wrap}, stylesheets=["https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap","/vet_tech.css","/mascote.css"],head_components=[rx.el.script(src="/preferences.js"),rx.el.script(src="/mascote.js",defer=True)])
app.add_page(attendance_content,route="/",on_load=Preview.setup)
