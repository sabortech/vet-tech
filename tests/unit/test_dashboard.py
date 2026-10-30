import asyncio
from datetime import date, timedelta
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import AsyncMock, patch

from reflex.istate.data import ReflexURL, RouterData

from test_auth_state import make_state
from vet_tech.features.auth.state import State
from vet_tech.features.dashboard.state import project_pet
from vet_tech.features.navigation.state import TUTOR_DESTINATIONS
from vet_tech.shared.xano_client import XanoRequestError


ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = ROOT / "xano" / "api" / "clinical" / "tutor" / "dashboard_GET.xs"


async def consume(generator):
    return [event async for event in generator]


def signed_in_state():
    state = make_state()
    state.profile = "tutor"
    state._auth_token = "synthetic-session"
    state.is_authenticated = True
    state.pets = [{"id": "1", "nome": "Pet 1"}, {"id": "2", "nome": "Pet 2"}]
    return state


def execute_dashboard_lambda(variables: dict[str, object]) -> dict[str, object]:
    source = ENDPOINT.read_text(encoding="utf-8")
    match = re.search(r'code = """(.*?)"""', source, re.DOTALL)
    if match is None:
        raise AssertionError("Dashboard Xano Lambda was not found.")
    runner = (
        "let s='';process.stdin.setEncoding('utf8');"
        "process.stdin.on('data',x=>s+=x);"
        "process.stdin.on('end',()=>{const d=JSON.parse(s);"
        "process.stdout.write(JSON.stringify(new Function('$var',d.code)(d.vars)));});"
    )
    result = subprocess.run(
        ["node", "-e", runner],
        input=json.dumps({"code": match.group(1), "vars": variables}),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


class DashboardProjectionTests(unittest.TestCase):
    def test_profile_age_and_optional_fields_are_derived_without_invention(self):
        row = {
            "id": 1,
            "nome": "Luna",
            "especie_nome": "Gato",
            "data_nasc": "2024-02-28",
            "peso_atual": 0,
            "foto": {"url": "https://example.invalid/luna.png"},
            "consultas": [],
            "vacinas": [],
            "exames": [],
        }
        projected = project_pet(row, date(2025, 2, 28))
        self.assertEqual(projected["idade"], "1 ano")
        self.assertEqual(projected["peso"], "0")
        self.assertEqual(projected["foto"], "https://example.invalid/luna.png")
        self.assertEqual(projected["raca"], "SRD")
        self.assertEqual(projected["proxima_vacina"], {})
        self.assertEqual(projected["ultima_consulta"], {})
        self.assertIn("Nenhum item de acompanhamento", projected["mensagem_acompanhamento"])

    def test_next_vaccine_last_finalized_consult_and_next_event_are_ordered(self):
        projected = project_pet(
            {
                "id": 3,
                "consultas": [
                    {"status": "finalizada", "data_atendimento": "2025-02-01"},
                    {"status": "finalizada", "data_atendimento": "2025-03-01"},
                    {"status": "agendada", "agendada_para": "2025-01-01"},
                    {"status": "finalizada", "retorno_previsto": "2025-04-02"},
                ],
                "vacinas": [
                    {"vacina": "Raiva", "data_prox_dose": "2025-04-03"},
                    {"vacina": "Múltipla", "data_prox_dose": "2025-04-02"},
                    {"vacina": "Antiga", "data_prox_dose": "2025-03-31"},
                ],
                "exames": [],
            },
            date(2025, 4, 2),
        )
        self.assertEqual(projected["ultima_consulta"]["data"], "01/03/2025")
        self.assertEqual(projected["proxima_vacina"]["nome"], "Múltipla")
        self.assertEqual(projected["proximo_evento"]["tipo"], "Retorno previsto")
        self.assertEqual(projected["proximo_evento"]["data"], "02/04/2025")
        self.assertEqual(len(projected["acompanhamentos"]), 1)

    def test_overdue_records_and_unrealized_exam_are_described_without_clinical_claims(self):
        projected = project_pet(
            {
                "consultas": [{"status": "finalizada", "retorno_previsto": "2025-04-01"}],
                "vacinas": [{"vacina": "Raiva", "data_prox_dose": "2025-04-01"}],
                "exames": [
                    {"tipo": "Imagem", "status": "solicitado", "data_solicitacao": "2025-04-01"},
                    {"tipo": "Hemograma", "status": "realizado"},
                ],
            },
            date(2025, 4, 2),
        )
        descriptions = [item["texto"] for item in projected["acompanhamentos"]]
        self.assertEqual(len(descriptions), 3)
        self.assertTrue(any("data registrada" in text.casefold() for text in descriptions))
        self.assertTrue(any("realização de Imagem não está registrada" in text for text in descriptions))
        self.assertEqual(projected["proximo_evento"], {"tipo": "", "data": ""})
        self.assertNotIn("saudável", projected["mensagem_acompanhamento"].casefold())
        self.assertNotIn("em dia", projected["mensagem_acompanhamento"].casefold())

    def test_recent_activity_is_date_sorted_and_limited_to_three_per_type(self):
        start = date(2025, 1, 1)
        projected = project_pet(
            {
                "consultas": [
                    {
                        "status": "finalizada",
                        "data_atendimento": (start + timedelta(days=day)).isoformat(),
                    }
                    for day in range(1000)
                ],
                "vacinas": [
                    {
                        "vacina": f"Vacina {day}",
                        "data_aplicacao": (start + timedelta(days=day)).isoformat(),
                    }
                    for day in range(1000)
                ],
            },
            date(2030, 1, 1),
        )
        self.assertEqual(len(projected["atividade_recente"]), 6)
        self.assertEqual(
            [row["tipo"] for row in projected["atividade_recente"]],
            ["Vacina", "Vacina", "Vacina", "Consulta", "Consulta", "Consulta"],
        )

    def test_missing_clinical_dates_do_not_create_events_or_raise(self):
        projected = project_pet(
            {
                "consultas": [
                    {"status": "finalizada"},
                    {"status": "agendada"},
                    {"status": "finalizada", "retorno_previsto": None},
                ],
                "vacinas": [
                    {"vacina": "Sem datas"},
                    {"vacina": "Sem próxima dose", "data_aplicacao": None},
                ],
                "exames": [
                    {"tipo": "Exame sem datas", "status": "solicitado"},
                ],
            },
            date(2025, 4, 2),
        )
        self.assertEqual(projected["proximo_evento"], {"tipo": "", "data": ""})
        self.assertEqual(projected["proxima_vacina"], {})
        self.assertEqual(projected["ultima_consulta"], {})
        self.assertEqual(projected["atividade_recente"], [])
        self.assertEqual([item["tipo"] for item in projected["acompanhamentos"]], ["exame"])

    def test_dashboard_endpoint_scopes_and_bounds_every_clinical_query(self):
        source = ENDPOINT.read_text(encoding="utf-8")
        self.assertIn('auth = "tutor"', source)
        self.assertIn('function.run "Clinical/assert_owner"', source)
        self.assertIn("pet_id: $input.pet_id", source)
        self.assertIn("tutor_id: $auth.id", source)
        self.assertIn("$db.pet.id == $owned_pet.id && $db.pet.tutor_id == $auth.id", source)
        self.assertNotIn("$var.pets|count", source)
        queries = re.findall(
            r"db\.query (consulta|vacina|exame) \{(.*?)\n    \} as \$",
            source,
            re.DOTALL,
        )
        self.assertGreaterEqual(len(queries), 8)
        for table, query in queries:
            self.assertIn('table: "pet"', query, table)
            self.assertIn("$db.pet.tutor_id == $auth.id", query, table)
            self.assertIn(f"$db.{table}.pet_id == $owned_pet.id", query, table)
            self.assertIn("paging:", query, table)
        self.assertIn("consulta.agendada_para: \"asc\"", source)
        self.assertIn("vacina.data_prox_dose: \"asc\"", source)
        self.assertIn("exame.data_realizacao == null", source)
        self.assertIn("per_page: 11", source)
        self.assertIn("acompanhamentos_truncados", source)
        self.assertIn("query \"tutor/dashboard\" verb=GET", source)
        self.assertIn('api_group = "Clinical"', source)
        self.assertIn("return = {", source)
        self.assertIn("rows.set(id,{...rows.get(id),...row})", source)
        self.assertNotIn('"especie_id"', source)
        self.assertNotIn('"diagnostico"', source)
        self.assertNotIn('"obs"', source)
        self.assertNotIn('"resultado"', source)
        self.assertNotIn('"arquivo"', source)

    def test_dashboard_endpoint_returns_single_pet_contract_and_merges_limited_rows(self):
        response = execute_dashboard_lambda({
            "pet": {
                "id": 7,
                "nome": "Luna",
                "especie_nome": "Gato",
                "data_nasc": "2023-02-01",
                "peso_atual": 4.2,
            },
            "next_consultations": [
                {"id": 1, "pet_id": 7, "status": "agendada", "agendada_para": "2030-01-01"}
            ],
            "next_returns": [
                {"id": 1, "pet_id": 7, "retorno_previsto": "2030-01-02"}
            ],
            "overdue_returns": [],
            "recent_attended_consultations": [],
            "recent_legacy_consultations": [],
            "next_vaccines": [{"id": 2, "pet_id": 7, "vacina": "Raiva", "data_prox_dose": "2030-01-03"}],
            "overdue_vaccines": [],
            "recent_vaccines": [{"id": 2, "pet_id": 7, "vacina": "Raiva", "data_aplicacao": "2029-01-03"}],
            "pending_exams": [
                {"id": exam_id, "pet_id": 7, "tipo": "Exame", "status": "solicitado"}
                for exam_id in range(10, 21)
            ],
        })

        self.assertEqual(response["id"], 7)
        self.assertEqual(response["nome"], "Luna")
        self.assertEqual(
            response["consultas"],
            [{
                "status": "agendada",
                "agendada_para": "2030-01-01",
                "retorno_previsto": "2030-01-02",
            }],
        )
        self.assertEqual(response["vacinas"], [{
            "vacina": "Raiva",
            "data_prox_dose": "2030-01-03",
            "data_aplicacao": "2029-01-03",
        }])
        self.assertEqual(len(response["exames"]), 10)
        self.assertTrue(response["acompanhamentos_truncados"])
        self.assertNotIn("pet_id", response["consultas"][0])


class DashboardStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_dashboard_load_redirects_unauthenticated_and_non_tutor_profiles(self):
        for authenticated, profile, destination in (
            (False, "", "/login"),
            (True, "veterinario", "/"),
        ):
            state = signed_in_state()
            state.is_authenticated = authenticated
            state.profile = profile
            with self.subTest(profile=profile), patch(
                "vet_tech.features.dashboard.state.xano_request",
                new_callable=AsyncMock,
            ) as request:
                events = await consume(State.load_dashboard.fn(state))
            request.assert_not_awaited()
            self.assertEqual(len(events), 1)
            self.assertIn(destination, str(events[0]))

    async def test_scope_changes_only_dashboard_and_rejects_unknown_pet(self):
        state = signed_in_state()
        state.selected_pet = {"id": "2"}
        context_generation = state._pet_context_generation
        row = {"id": 1, "nome": "Pet 1", "consultas": [], "vacinas": [], "exames": []}
        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
            return_value=row,
        ) as request:
            await consume(State.set_dashboard_scope.fn(state, "1"))
        self.assertEqual(state.dashboard_scope, "1")
        request.assert_awaited_once_with(
            "GET",
            "vettech-clinical",
            "tutor/dashboard?pet_id=1",
            auth_token="synthetic-session",
        )
        await consume(State.set_dashboard_scope.fn(state, "foreign"))
        self.assertEqual(state.dashboard_scope, "1")
        self.assertEqual(state.selected_pet_id, "2")
        self.assertEqual(state._pet_context_generation, context_generation)

    async def test_individual_scope_fetches_only_selected_pet(self):
        state = signed_in_state()
        state.dashboard_scope = "2"
        row = {"id": 2, "nome": "Dois", "consultas": [], "vacinas": [], "exames": []}
        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
            return_value=row,
        ) as request:
            await consume(State.load_dashboard.fn(state))
        request.assert_awaited_once_with(
            "GET",
            "vettech-clinical",
            "tutor/dashboard?pet_id=2",
            auth_token="synthetic-session",
        )
        self.assertEqual(state.dashboard_scope, "2")
        self.assertEqual([pet["id"] for pet in state.dashboard_pets], ["2"])
        self.assertFalse(state.dashboard_loading)
        self.assertEqual(state.dashboard_error, "")

    async def test_all_pets_scope_fetches_each_owned_pet_and_empty_tutor_makes_no_request(self):
        state = signed_in_state()

        async def request(_method, _group, endpoint, **_kwargs):
            pet_id = endpoint.rsplit("=", 1)[1]
            return {
                "id": int(pet_id),
                "nome": f"Pet {pet_id}",
                "consultas": [],
                "vacinas": [],
                "exames": [],
            }

        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
            side_effect=request,
        ) as mock_request:
            await consume(State.load_dashboard.fn(state))
        self.assertEqual(
            {call.args[2] for call in mock_request.await_args_list},
            {"tutor/dashboard?pet_id=1", "tutor/dashboard?pet_id=2"},
        )
        self.assertEqual([pet["id"] for pet in state.dashboard_pets], ["1", "2"])

        state.pets = []
        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
        ) as empty_request:
            await consume(State.load_dashboard.fn(state))
        empty_request.assert_not_awaited()
        self.assertEqual(state.dashboard_pets, [])
        self.assertEqual(state.dashboard_error, "")

    async def test_all_pets_reads_are_limited_to_four_concurrent_requests(self):
        state = signed_in_state()
        state.pets = [{"id": str(pet_id)} for pet_id in range(1, 10)]
        active = maximum_active = 0

        async def request(_method, _group, endpoint, **_kwargs):
            nonlocal active, maximum_active
            active += 1
            maximum_active = max(maximum_active, active)
            await asyncio.sleep(0.01)
            active -= 1
            pet_id = endpoint.rsplit("=", 1)[1]
            return {"id": int(pet_id), "consultas": [], "vacinas": [], "exames": []}

        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
            side_effect=request,
        ):
            await consume(State.load_dashboard.fn(state))
        self.assertGreater(maximum_active, 1)
        self.assertLessEqual(maximum_active, 4)
        self.assertEqual(len(state.dashboard_pets), 9)

    async def test_pet_owned_by_another_tutor_returns_error_without_dashboard_data(self):
        state = signed_in_state()
        state.dashboard_scope = "2"
        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
            side_effect=XanoRequestError("Pet não disponível.", status_code=404),
        ) as request:
            await consume(State.load_dashboard.fn(state))
        request.assert_awaited_once_with(
            "GET",
            "vettech-clinical",
            "tutor/dashboard?pet_id=2",
            auth_token="synthetic-session",
        )
        self.assertEqual(state.dashboard_pets, [])
        self.assertEqual(state.dashboard_error, "Pet não disponível.")

    async def test_truncated_followups_are_explained_to_tutor(self):
        projected = project_pet(
            {
                "id": 1,
                "acompanhamentos_truncados": True,
                "consultas": [],
                "vacinas": [{"vacina": "Raiva", "data_prox_dose": "2025-04-01"}],
                "exames": [],
            },
            date(2025, 4, 2),
        )
        self.assertTrue(projected["acompanhamentos_truncados"])
        self.assertIn("lista exibida é limitada", projected["mensagem_acompanhamento"])

    async def test_failed_read_shows_error_instead_of_empty_state(self):
        state = signed_in_state()
        with patch(
            "vet_tech.features.dashboard.state.xano_request",
            new_callable=AsyncMock,
            side_effect=XanoRequestError("Falha de leitura", status_code=503),
        ):
            await consume(State.load_dashboard.fn(state))
        self.assertEqual(state.dashboard_pets, [])
        self.assertIn("Falha de leitura", state.dashboard_error)
        self.assertFalse(state.dashboard_loading)

    async def test_late_response_after_logout_cannot_restore_dashboard_data(self):
        state = signed_in_state()
        started, release = asyncio.Event(), asyncio.Event()

        async def request(*args, **kwargs):
            started.set()
            await release.wait()
            return {"id": 1, "nome": "Antigo", "consultas": [], "vacinas": [], "exames": []}

        with patch("vet_tech.features.dashboard.state.xano_request", side_effect=request):
            pending = State.load_dashboard.fn(state)
            await pending.__anext__()
            task = asyncio.create_task(consume(pending))
            await started.wait()
            state._clear_session()
            release.set()
            await task
        self.assertEqual(state.dashboard_pets, [])
        self.assertFalse(state.is_authenticated)
        self.assertFalse(state.dashboard_loading)

    async def test_late_response_after_scope_change_cannot_replace_selected_pet(self):
        state = signed_in_state()
        started_old, release_old = asyncio.Event(), asyncio.Event()
        started_new, release_new = asyncio.Event(), asyncio.Event()

        async def request(_method, _group, endpoint, **_kwargs):
            pet_id = endpoint.rsplit("=", 1)[1]
            if pet_id == "1":
                started_old.set()
                await release_old.wait()
            else:
                started_new.set()
                await release_new.wait()
            return {
                "id": int(pet_id),
                "nome": f"Pet {pet_id}",
                "consultas": [],
                "vacinas": [],
                "exames": [],
            }

        with patch("vet_tech.features.dashboard.state.xano_request", side_effect=request):
            old_read = State.set_dashboard_scope.fn(state, "1")
            await old_read.__anext__()
            old_task = asyncio.create_task(consume(old_read))
            await started_old.wait()

            new_read = State.set_dashboard_scope.fn(state, "2")
            await new_read.__anext__()
            new_task = asyncio.create_task(consume(new_read))
            await started_new.wait()
            release_new.set()
            await new_task

            self.assertEqual(state.dashboard_scope, "2")
            self.assertEqual([pet["id"] for pet in state.dashboard_pets], ["2"])

            release_old.set()
            await old_task

        self.assertEqual(state.dashboard_scope, "2")
        self.assertEqual([pet["id"] for pet in state.dashboard_pets], ["2"])
        self.assertEqual(state.dashboard_error, "")
        self.assertFalse(state.dashboard_loading)

    async def test_late_error_after_scope_change_cannot_replace_current_result(self):
        state = signed_in_state()
        started_old, release_old = asyncio.Event(), asyncio.Event()
        started_new, release_new = asyncio.Event(), asyncio.Event()

        async def request(_method, _group, endpoint, **_kwargs):
            pet_id = endpoint.rsplit("=", 1)[1]
            if pet_id == "1":
                started_old.set()
                await release_old.wait()
                raise XanoRequestError("Falha antiga", status_code=503)
            started_new.set()
            await release_new.wait()
            return {"id": 2, "nome": "Pet 2", "consultas": [], "vacinas": [], "exames": []}

        with patch("vet_tech.features.dashboard.state.xano_request", side_effect=request):
            old_read = State.set_dashboard_scope.fn(state, "1")
            await old_read.__anext__()
            old_task = asyncio.create_task(consume(old_read))
            await started_old.wait()

            new_read = State.set_dashboard_scope.fn(state, "2")
            await new_read.__anext__()
            new_task = asyncio.create_task(consume(new_read))
            await started_new.wait()
            release_new.set()
            await new_task
            release_old.set()
            await old_task

        self.assertEqual(state.dashboard_scope, "2")
        self.assertEqual([pet["id"] for pet in state.dashboard_pets], ["2"])
        self.assertEqual(state.dashboard_error, "")
        self.assertFalse(state.dashboard_loading)

    async def test_late_error_after_logout_cannot_restore_dashboard_error(self):
        state = signed_in_state()
        state.dashboard_scope = "1"
        started, release = asyncio.Event(), asyncio.Event()

        async def request(*_args, **_kwargs):
            started.set()
            await release.wait()
            raise XanoRequestError("Falha após logout", status_code=503)

        with patch("vet_tech.features.dashboard.state.xano_request", side_effect=request):
            pending = State.load_dashboard.fn(state)
            await pending.__anext__()
            task = asyncio.create_task(consume(pending))
            await started.wait()
            state._clear_session()
            release.set()
            await task

        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.dashboard_pets, [])
        self.assertEqual(state.dashboard_error, "")
        self.assertFalse(state.dashboard_loading)

    async def test_clinical_actions_require_a_pet_in_both_authorized_lists(self):
        state = signed_in_state()
        state.dashboard_pets = [{"id": "1"}]
        with patch("vet_tech.features.dashboard.state.rx.redirect") as redirect:
            State.dashboard_open_clinical.fn(state, "1", "vacinas")
            redirect.assert_called_once_with("/prontuario?secao=vacinas&pet_id=1")
        with patch("vet_tech.features.dashboard.state.rx.redirect") as redirect:
            State.dashboard_open_clinical.fn(state, "foreign", "vacinas")
            redirect.assert_not_called()
            State.dashboard_open_clinical.fn(state, "1", "exames")
            redirect.assert_not_called()

    async def test_booking_action_sets_explicit_pet_without_changing_clinical_selection(self):
        state = signed_in_state()
        state.dashboard_pets = [{"id": "1"}, {"id": "2"}]
        state.selected_pet = {"id": "1"}
        with patch(
            "vet_tech.features.clinical.state.xano_request",
            new_callable=AsyncMock,
            return_value=[{"id": 9, "nome": "Profissional"}],
        ):
            await consume(State.dashboard_book_pet.fn(state, "2"))
        self.assertTrue(state.booking_open)
        self.assertEqual(state.booking_pet, "2")
        self.assertEqual(state.selected_pet_id, "1")
        self.assertEqual(state.booking_professionals[0]["id"], "9")

    async def test_explicit_clinical_route_context_selects_only_own_pet(self):
        state = signed_in_state()
        state.selected_pet = {"id": "1"}
        state.router = RouterData(
            url=ReflexURL("http://localhost/prontuario?secao=vacinas&pet_id=2")
        )
        event = State.enter_clinical_page.fn(state)
        self.assertIsNotNone(event)
        self.assertEqual(state.active_section, "Vacinas")
        self.assertEqual(state.pet_target_id, "2")
        self.assertEqual(state.selected_pet_id, "")
        self.assertTrue(state.is_loading_pet)

        state.router = RouterData(
            url=ReflexURL("http://localhost/prontuario?secao=vacinas&pet_id=foreign")
        )
        event = State.enter_clinical_page.fn(state)
        self.assertIsNone(event)
        self.assertEqual(state.selected_pet, {})
        self.assertTrue(state.pet_picker_open)
        self.assertEqual(state.pet_detail_message, "Pet não disponível.")

    def test_dashboard_is_allowed_as_tutor_destination(self):
        self.assertIn("/dashboard", TUTOR_DESTINATIONS)


if __name__ == "__main__":
    unittest.main()
