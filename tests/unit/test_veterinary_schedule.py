"""Agenda projections and existing clinical event contracts with synthetic data."""
import unittest
from unittest.mock import AsyncMock, patch

from test_clinical_state import session, consume, TARGET
from test_clinical_projections import execute
from vet_tech.features.auth.state import State
from vet_tech.features.clinical.state import agenda_photo


class VeterinaryScheduleTests(unittest.IsolatedAsyncioTestCase):
    async def test_initial_agenda_selects_today(self):
        from vet_tech.features.clinical.state import today
        state = session("veterinario")
        state.agenda_day = ""
        with patch(TARGET, new_callable=AsyncMock, return_value={"items": [], "total": 0}):
            await consume(State.load_agenda.fn(state))
        self.assertEqual(state.agenda_day, today())

    async def test_week_and_day_navigation_cross_month_and_reset_page(self):
        state = session("veterinario")
        state.agenda_day = "2030-01-31"
        state.agenda_page = 2
        self.assertEqual(state.agenda_week[0]["date"], "2030-01-28")
        self.assertIn("31 de janeiro de 2030", state.agenda_date_label)
        with patch(TARGET, new_callable=AsyncMock, return_value={"items": [], "total": 0}) as request:
            await consume(State.agenda_day_by.fn(state, 1))
        self.assertEqual(state.agenda_day, "2030-02-01")
        self.assertEqual(state.agenda_page, 1)
        self.assertIn("dia=2030-02-01", request.call_args.args[2])

    async def test_agenda_covers_outside_hours_and_maps_real_status(self):
        from datetime import datetime
        rows = [{"id": i, "pet_id": 5, "pet_nome": "Synthetic", "status": status,
                 "agendada_para": int(datetime.fromisoformat(f"2030-01-11T{time}:00-03:00").timestamp() * 1000)}
                for i, (time, status) in enumerate([("07:30", "agendada"), ("10:15", "em_atendimento"), ("10:45", "finalizada"), ("19:00", "agendada")], 1)]
        state = session("veterinario")
        state.vet_section, state.agenda_day = "Horários", "2030-01-11"
        with patch(TARGET, new_callable=AsyncMock, return_value={"items": rows, "total": 27}):
            await consume(State.load_agenda.fn(state))
        self.assertEqual(state.agenda_hours, list(range(7, 20)))
        self.assertEqual([r["hora"] for r in state.agenda_rows], ["07:30", "10:15", "10:45", "19:00"])
        self.assertEqual(state.agenda_completed, 1)
        self.assertEqual(state.agenda_in_progress, 1)
        self.assertEqual(state.agenda_total, 27)
        self.assertEqual(state.agenda_rows[2]["status_label"], "Concluída")

    async def test_revoked_photo_is_never_rendered_even_if_response_has_one(self):
        state = session("veterinario")
        with patch(TARGET, new_callable=AsyncMock, return_value={"items": [{"id": 1, "status": "agendada", "agendada_para": 1893544200000,
                    "autorizado": False, "pet_foto": "https://example.invalid/private.jpg"}], "total": 1}):
            await consume(State.load_agenda.fn(state))
        self.assertEqual(state.agenda_rows[0]["pet_foto"], "")

    def test_backend_adds_photo_only_for_active_consent(self):
        variables = {"reservations": [{"id": 1, "pet_id": 5, "status": "agendada", "agendada_para": 1893544200000, "motivo": "Private"}],
                     "consents": [{"pet_id": 5}], "pets": [{"id": 5, "nome": "Synthetic", "foto": "data:image/png;base64,c3ludGhldGlj"}]}
        result = execute("xano/api/clinical/agenda_GET.xs", {"page": 1}, variables)
        self.assertEqual(result["items"][0]["pet_foto"], variables["pets"][0]["foto"])
        variables["consents"] = []
        result = execute("xano/api/clinical/agenda_GET.xs", {"page": 1}, variables)
        self.assertEqual(set(result["items"][0]), {"id", "status", "agendada_para", "autorizado"})

    def test_photo_accepts_existing_formats_and_rejects_uri_code(self):
        self.assertEqual(agenda_photo("javascript:alert(1)"), "")
        self.assertEqual(agenda_photo(None), "")
        self.assertEqual(agenda_photo("data:image/svg+xml;base64,abc"), "")
        self.assertEqual(agenda_photo("data:image/png;base64,abc"), "data:image/png;base64,abc")

class VeterinaryCalendarTests(unittest.IsolatedAsyncioTestCase):
    def test_open_browse_and_cancel_preserve_agenda_without_request(self):
        state = session("veterinario")
        state.agenda_day = "2030-01-11"
        with patch(TARGET, new_callable=AsyncMock) as request:
            State.agenda_calendar_set_open.fn(state, True)
            self.assertEqual(state.agenda_calendar_month, "2030-01")
            State.agenda_calendar_shift.fn(state, -1)
            self.assertEqual(state.agenda_calendar_month, "2029-12")
            State.agenda_calendar_set_open.fn(state, False)
            self.assertFalse(state.agenda_calendar_open)
            self.assertEqual(state.agenda_day, "2030-01-11")
            request.assert_not_called()

    def test_leap_year_and_year_month_selection(self):
        state = session("veterinario")
        state.agenda_calendar_month = "2028-02"
        days = state.agenda_calendar_days
        self.assertEqual(len(days), 42)
        self.assertIn("2028-02-29", [d["date"] for d in days])
        State.agenda_calendar_choose_year.fn(state, "2029")
        self.assertNotIn("2029-02-29", [d["date"] for d in state.agenda_calendar_days])
        State.agenda_calendar_choose_month.fn(state, "Dezembro")
        State.agenda_calendar_shift.fn(state, 1)
        self.assertEqual(state.agenda_calendar_month, "2030-01")
        State.agenda_calendar_choose_year.fn(state, "invalid")
        self.assertEqual(state.agenda_calendar_month, "2030-01")

    async def test_select_past_day_closes_dialog_and_resets_pagination(self):
        state = session("veterinario")
        state.agenda_calendar_open = True
        state.agenda_page = 3
        with patch(TARGET, new_callable=AsyncMock, return_value={"items": [], "total": 0}) as request:
            await consume(State.agenda_choose_day.fn(state, "2020-02-29"))
        self.assertEqual(state.agenda_day, "2020-02-29")
        self.assertFalse(state.agenda_calendar_open)
        self.assertEqual(state.agenda_page, 1)
        self.assertIn("dia=2020-02-29", request.call_args.args[2])

    def test_session_cleanup_and_role_guard(self):
        state = session("veterinario")
        State.agenda_calendar_set_open.fn(state, True)
        state._clear_clinical_session()
        self.assertFalse(state.agenda_calendar_open)
        self.assertEqual(state.agenda_calendar_month, "")
        state.profile = "tutor"
        State.agenda_calendar_set_open.fn(state, True)
        State.agenda_calendar_shift.fn(state, 1)
        self.assertFalse(state.agenda_calendar_open)
        self.assertEqual(state.agenda_calendar_month, "")

    def test_month_navigation_stays_inside_supported_years(self):
        state = session("veterinario")
        for month, offset in [("0001-01", -1), ("9999-12", 1)]:
            state.agenda_calendar_month = month
            State.agenda_calendar_shift.fn(state, offset)
            self.assertEqual(state.agenda_calendar_month, month)
            self.assertEqual(len(state.agenda_calendar_days), 42)


if __name__ == "__main__":
    unittest.main()
