"""Datas técnicas, apresentação brasileira e isolamento de fuso."""

from datetime import date, datetime, timezone
import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state, submit_pet
from vet_tech.features.auth.state import State, format_pet_birth_date
from vet_tech.features.clinical.state import cards
from vet_tech.features.dashboard.state import project_pet
from vet_tech.shared.dates import calendar_date, date_label, instant_label


class DateContractTests(unittest.TestCase):
    def test_calendar_dates_keep_their_day_and_never_guess_slash_format(self):
        self.assertEqual(date_label("2026-04-03"), "03/04/2026")
        self.assertEqual(date_label("2026-04-23"), "23/04/2026")
        self.assertEqual(date_label("2024-02-29"), "29/02/2024")
        for value in ("03/04/2026", "2026-02-29", "2026-04-31", "20260403", None, True, 1775174400000):
            with self.subTest(value=value):
                self.assertIsNone(calendar_date(value))

    def test_civil_iso_with_offset_does_not_shift_birth_or_vaccine_day(self):
        for offset in ("Z", "-03:00", "+14:00"):
            self.assertEqual(date_label("2026-04-03T00:00:00" + offset), "03/04/2026")
            self.assertEqual(format_pet_birth_date("2026-04-03T00:00:00" + offset), "03/04/2026")

    def test_instants_use_business_timezone_and_keep_time_for_iso_and_numbers(self):
        value = "2026-04-03T01:30:00Z"
        milliseconds = int(datetime(2026, 4, 3, 1, 30, tzinfo=timezone.utc).timestamp() * 1000)
        for instant in (value, milliseconds, str(milliseconds)):
            self.assertEqual(instant_label(instant), "02/04/2026 22:30")
        self.assertEqual(instant_label("2026-04-03T08:00:00-03:00"), "03/04/2026 08:00")
        self.assertEqual(instant_label("2026-04-03"), "03/04/2026")

    def test_cards_distinguish_instant_fields_from_calendar_fields(self):
        row = cards([{"agendada_para": "2026-04-03T01:30:00Z",
                      "ocorrido_em": "2026-04-03T01:30:00Z",
                      "iniciada_em": "2026-04-03T01:30:00Z",
                      "data_prox_dose": "2026-04-03", "data_realizacao": "2026-04-23"}])[0]
        self.assertEqual(row["quando"], "02/04/2026 22:30")
        self.assertEqual(row["ocorrido_em_legivel"], "02/04/2026 22:30")
        self.assertEqual(row["iniciada_em_legivel"], "02/04/2026 22:30")
        self.assertEqual(row["data_prox_dose_legivel"], "03/04/2026")
        self.assertEqual(row["data_realizacao_legivel"], "23/04/2026")

    def test_dashboard_vaccine_from_today_wins_without_inventing_missing_next_dose(self):
        projected = project_pet({"vacinas": [
            {"vacina": "Aplicada sem próxima dose", "data_aplicacao": "2026-04-01"},
            {"vacina": "Futura", "data_prox_dose": "2026-04-23"},
            {"vacina": "Hoje", "data_prox_dose": "2026-04-03"},
            {"vacina": "Passada", "data_prox_dose": "2026-04-02"},
        ]}, date(2026, 4, 3))
        self.assertEqual(projected["proxima_vacina"], {"nome": "Hoje", "data": "03/04/2026"})
        self.assertEqual(len(projected["acompanhamentos"]), 1)

    def test_dashboard_empty_card_has_all_rendered_keys(self):
        projected = project_pet({"vacinas": [
            {"vacina": "Aplicada", "data_aplicacao": "2026-04-01", "data_prox_dose": None}
        ]}, date(2026, 4, 3))
        self.assertEqual(projected["proxima_vacina"], {"nome": "", "data": ""})
        self.assertEqual(projected["ultima_consulta"]["data"], "")
        self.assertEqual(projected["atividade_recente"][0]["nome"], "Aplicada")

    def test_recent_activity_sorts_raw_dates_across_months_and_years(self):
        projected = project_pet({
            "consultas": [{"status": "finalizada", "data_atendimento": "2026-10-31"}],
            "vacinas": [{"vacina": "Antiga", "data_aplicacao": "2025-12-31"}],
        }, date(2026, 11, 1))
        self.assertEqual([r["data"] for r in projected["atividade_recente"]], ["31/10/2026", "31/12/2025"])

    def test_scheduled_instant_is_compared_in_the_business_day(self):
        row = {"consultas": [{"status": "agendada", "agendada_para": "2026-04-03T01:30:00Z"}]}
        self.assertEqual(project_pet(row, date(2026, 4, 2))["proximo_evento"]["data"], "02/04/2026")
        self.assertEqual(project_pet(row, date(2026, 4, 3))["proximo_evento"]["data"], "")


class PetDateSubmissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_birth_date_is_not_sent(self):
        state = make_state()
        state.is_authenticated = True
        state._auth_token = "synthetic"
        state.pet_name, state.selected_species_id = "Sintético", "1"
        state.pet_birth_date = "03/04/2026"
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock) as request:
            await submit_pet(state, [])
        request.assert_not_awaited()
        self.assertIn("data de nascimento válida", state.pet_message)

    async def test_selected_birth_date_is_sent_as_iso(self):
        state = make_state()
        state.is_authenticated = True
        state._auth_token = "synthetic"
        state.pet_name, state.selected_species_id = "Sintético", "1"
        state.pet_birth_date = "2026-04-03"
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value={"id": 1}) as request, \
             patch.object(State, "_load_pets", new_callable=AsyncMock):
            await submit_pet(state, [])
        self.assertEqual(request.call_args.kwargs["json_payload"]["data_nasc"], "2026-04-03")
