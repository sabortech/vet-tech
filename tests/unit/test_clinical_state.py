import asyncio
from copy import deepcopy
import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError

TARGET = "vet_tech.features.clinical.state.xano_request"


def session(profile="tutor"):
    state = make_state()
    state.profile = profile
    state._auth_token = "synthetic-session"
    state.is_authenticated = True
    return state


async def consume(generator):
    return [event async for event in generator]


class ClinicalStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_pending_history_cannot_restore_data_after_access_denial(self):
        state = session("veterinario")
        started, release = asyncio.Event(), asyncio.Event()

        async def request(*args, **kwargs):
            started.set()
            await release.wait()
            return {"pet": {"nome": "Synthetic"}, "historico": {"consultas": [{"id": 1}]}}

        with patch(TARGET, side_effect=request):
            pending = asyncio.create_task(State.open_prior_history.fn(state, "1"))
            await started.wait()
            state._clinic_error(XanoRequestError("Revoked", status_code=403))
            release.set()
            await pending
        self.assertEqual(state.prior_history, {})
        self.assertEqual(state.prior_pet_info, {})

    async def test_basic_pet_info_keeps_zero_and_clears_on_expiration(self):
        from vet_tech.features.clinical.state import pet_summary
        state = session("veterinario")
        state.clinical_pet_info = pet_summary({"nome": "Synthetic", "peso_atual": 0, "data_nasc": "2020-01-02"})
        self.assertEqual(state.clinical_pet_info["peso"], "0")
        self.assertEqual(state.clinical_pet_info["nascimento"], "02/01/2020")
        state._clinic_error(XanoRequestError("Expired", status_code=401))
        self.assertEqual(state.clinical_pet_info, {})
        self.assertEqual(state.prior_pet_info, {})

    async def test_actual_consultation_date_is_distinct_from_booking_date(self):
        from vet_tech.features.clinical.state import cards
        row = cards([{"id": 1, "data_atendimento": "2026-10-21", "agendada_para": "2026-10-28"}])[0]
        self.assertEqual(row["quando"], "28/10/2026")
        self.assertEqual(row["data_atendimento_legivel"], "21/10/2026")

    async def test_unsaved_changes_require_explicit_discard(self):
        state = session("veterinario")
        State.clinical_field.fn(state, "diagnostico", "Synthetic")
        self.assertTrue(state.clinical_dirty)
        self.assertIsNone(State.leave_attendance.fn(state, False))
        self.assertTrue(state.clinical_confirm_leave)
        self.assertIsNotNone(State.leave_attendance.fn(state, True))
        self.assertFalse(state.clinical_dirty)

    async def test_today_action_loads_actual_service_day(self):
        from vet_tech.features.clinical.state import today
        state = session("veterinario")
        state.vet_section = "Horários"
        state.agenda_day = "2030-01-01"
        with patch(TARGET, new_callable=AsyncMock, return_value={"items": [], "total": 0}) as request:
            await consume(State.agenda_today.fn(state))
        self.assertIn("dia=" + today(), request.call_args.args[2])
        self.assertEqual(state.agenda_day, today())

    async def test_dialog_opens_without_global_pet_and_cancel_never_writes(self):
        state = session()
        with patch(TARGET, new_callable=AsyncMock) as request:
            State.booking_set_open.fn(state, True)
            self.assertTrue(state.booking_open)
            self.assertEqual(state.booking_step, 1)
            state.booking_pet = "22"
            State.booking_set_open.fn(state, False)
        request.assert_not_awaited()
        self.assertEqual(state.selected_pet_id, "")
        self.assertEqual(state.booking_pet, "")

    async def test_back_preserves_all_booking_fields(self):
        state = session()
        state.booking_step = 2
        state.booking_day, state.booking_time = "2030-01-11", "08:00"
        state.booking_pet, state.booking_reason = "22", "Synthetic"
        State.booking_back.fn(state)
        self.assertEqual(state.booking_step, 1)
        self.assertEqual((state.booking_pet, state.booking_reason), ("22", "Synthetic"))

    async def test_old_professional_search_cannot_replace_new_pet_search(self):
        state = session()
        started, release = asyncio.Event(), asyncio.Event()

        async def request(method, group, endpoint, **kwargs):
            if endpoint.endswith("pet_id=1"):
                started.set()
                await release.wait()
                return [{"id": 1, "nome": "Old"}]
            return [{"id": 2, "nome": "Current"}]

        with patch(TARGET, side_effect=request):
            pending = asyncio.create_task(State.booking_choose_pet.fn(state, "1"))
            await started.wait()
            await State.booking_choose_pet.fn(state, "2")
            release.set()
            await pending
        self.assertEqual(state.booking_pet, "2")
        self.assertEqual(state.booking_professionals[0]["id"], "2")

    async def test_booking_timeout_retries_same_payload_and_blocks_double_click(self):
        state = session()
        state.selected_pet = {"id": "11"}
        State.booking_set_open.fn(state, True)
        state.booking_pet, state.booking_professional = "22", "3"
        state.booking_day, state.booking_time = "2030-01-11", "08:00"
        state.booking_reason = "Synthetic"
        calls = []

        async def request(*args, **kwargs):
            calls.append(deepcopy(kwargs["json_payload"]))
            if len(calls) == 1:
                raise XanoRequestError("Timeout")
            return {"id": 5, "status": "agendada"}

        with patch(TARGET, side_effect=request):
            first = State.booking_submit.fn(state)
            await first.__anext__()
            await consume(State.booking_submit.fn(state))
            self.assertEqual(calls, [])
            await consume(first)
            State.set_booking_reason.fn(state, "Changed")
            State.booking_set_open.fn(state, False)
            self.assertTrue(state.booking_open)
            await consume(State.booking_submit.fn(state))
        self.assertEqual(calls[0], calls[1])
        self.assertEqual(calls[0]["payload"]["pet_id"], "22")
        self.assertEqual(state.selected_pet_id, "11")
        self.assertFalse(state.booking_open)

    async def test_old_history_response_is_discarded_on_global_pet_change(self):
        state = session()
        state.selected_pet = {"id": "1"}
        started, release = asyncio.Event(), asyncio.Event()

        async def request(*args, **kwargs):
            started.set()
            await release.wait()
            return {} if args[2].endswith("historico") else []

        with patch(TARGET, side_effect=request):
            await consume(State.load_tutor_clinical.fn(state))
            with patch.object(State, '__aenter__', AsyncMock(return_value=state)), patch.object(State, '__aexit__', AsyncMock(return_value=False)):
                pending = asyncio.create_task(State.fetch_tutor_clinical.fn(state, state._clinic_generation, False))
                await started.wait()
                state._clear_pet_context()
                state.selected_pet = {"id": "2"}
                release.set()
                await pending
        self.assertEqual(state.history_rows, {})
        self.assertEqual(state._tutor_history_pet, "")

    async def test_lost_finalize_response_is_reconciled_without_second_post(self):
        state = session("veterinario")
        state.clinical_id = "7"
        state.clinical_status = "em_atendimento"
        state.clinical_version = 2
        with patch(TARGET, new_callable=AsyncMock, side_effect=XanoRequestError("Timeout")):
            await consume(State.save_attendance.fn(state, True))
        self.assertTrue(state._save_uncertain)
        with patch(TARGET, new_callable=AsyncMock, return_value={"consulta": {"status": "finalizada", "versao": 3}}) as request:
            await consume(State.save_attendance.fn(state, True))
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertEqual(state.clinical_status, "finalizada")
        self.assertFalse(state.clinical_dirty)

    async def test_expiration_clears_clinical_data_and_late_reply_cannot_restore_it(self):
        state = session("veterinario")
        state.clinical_id, state.clinical_diagnosis = "7", "Synthetic"
        state.prior_history = {"consultas": [{"id": "7"}]}
        state._clinic_error(XanoRequestError("Expired", status_code=401))
        self.assertEqual(state.clinical_id, "")
        self.assertEqual(state.clinical_diagnosis, "")
        self.assertEqual(state.prior_history, {})
        self.assertEqual(state._auth_token, "")

    async def test_published_detail_and_sections_share_ids(self):
        state = session()
        state.history_rows = {"consultas": [{"id": "7"}], "vacinas": [
            {"id": "12", "consulta_id": "7"}, {"id": "13", "consulta_id": "8"}]}
        State.show_consultation_detail.fn(state, "7")
        self.assertEqual(state.detail_sections["vacinas"], [{"id": "12", "consulta_id": "7"}])


if __name__ == "__main__":
    unittest.main()
