"""Prévia isolada: copiar para preview/preview.py em /tmp; nunca importar no app real."""
import os
import sys
sys.path.insert(0,os.environ["VET_TECH_SOURCE_ROOT"])
import reflex as rx
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import attendance_content
from vet_tech.components.veterinary_schedule import schedule_content
from vet_tech.components.mascote_flutuante import mascote_app_wrap
import asyncio
import vet_tech.features.clinical.state as clinical
_calls = 0
async def fake_history(*args, **kwargs):
    global _calls
    _calls += 1
    await asyncio.sleep(1)
    if _calls == 2:
        raise ValueError("Falha sintética ao consultar histórico")
    groups = {key: [] for key in ("consultas", "vacinas", "medicamentos", "doencas", "exames")}
    if _calls != 4:
        groups["consultas"] = [{"data_atendimento":"2026-10-01", "diagnostico":"Avaliação sintética anterior", "obs":"Paciente em acompanhamento."} for _ in range(8)]
        groups["vacinas"] = [{"vacina":"Vacina sintética", "data_aplicacao":"2026-10-01"}]
    return {"pet":{"nome":"Jessy", "sexo":"Feminino", "data_nasc":"2026-01-31", "peso_atual":10}, "historico":groups}
clinical.xano_request = fake_history
class Preview(rx.State):
    @rx.event
    async def setup(self):
        state = await self.get_state(State)
        state._auth_token = "synthetic-preview-only"
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

# The calendar browser suite checks this shared presentation without loading Xano.
app.add_page(schedule_content,route="/agenda",on_load=Preview.setup)
