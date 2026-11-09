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
    async def test_history_failure_and_retry_do_not_hide_agenda_or_change_attendance(self):
        state = session("veterinario")
        state.clinical_pet_id = "1"
        state.clinical_diagnosis = "Draft remains"
        state.agenda_rows = [{"id":"43", "pet_id":"2"}]
        with patch(TARGET, new_callable=AsyncMock, side_effect=XanoRequestError("Synthetic history failure", status_code=500)) as request:
            await State.open_prior_history.fn(state, "2")
            self.assertEqual(request.call_args.args[2], "veterinario/pets/2/historico")
        self.assertEqual(state.clinic_message, "")
        self.assertEqual(state.prior_history_message, "Synthetic history failure")
        self.assertEqual(state.agenda_rows, [{"id":"43", "pet_id":"2"}])
        self.assertEqual(state.clinical_diagnosis, "Draft remains")
        State.prepare_prior_history.fn(state)
        with patch(TARGET, new_callable=AsyncMock, return_value={"pet":{"nome":"Nina"},"historico":{"consultas":[]}}) as request:
            await State.open_prior_history.fn(state, "2")
            self.assertEqual(request.call_args.args[2], "veterinario/pets/2/historico")
        self.assertEqual(state.prior_pet_info["nome"], "Nina")
        self.assertEqual(state.prior_history_message, "")
        self.assertEqual(state.clinical_pet_id, "1")

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


class ConsultationPDFStateTests(unittest.IsolatedAsyncioTestCase):
    def prepare(self):
        state=session();state.selected_pet={'id':'7'};state.active_section='Consultas'
        state.detail_id='42';state.detail={'id':'42','status':'finalizada'}
        from test_consultation_pdf import export_payload
        from vet_tech.features.clinical.consultation_pdf import map_consultation_document
        State.open_consultation_pdf.fn(state)
        state._set_pdf_preview(map_consultation_document(export_payload(), 7, 42))
        state.pdf_preview_loading = False
        State.request_consultation_pdf.fn(state)
        return state

    def locks(self,state):
        from contextlib import ExitStack
        stack=ExitStack()
        stack.enter_context(patch.object(State,'__aenter__',AsyncMock(return_value=state)))
        stack.enter_context(patch.object(State,'__aexit__',AsyncMock(return_value=False)))
        return stack

    async def test_success_duplicate_click_and_retry_operation_key(self):
        from test_consultation_pdf import export_payload
        state=self.prepare();generation=state._pdf_generation;key=state._pdf_key
        self.assertIsNone(State.request_consultation_pdf.fn(state))
        with self.locks(state),patch(TARGET,new_callable=AsyncMock,side_effect=XanoRequestError('secret',status_code=500)):
            self.assertEqual(await consume(State.generate_consultation_pdf.fn(state,generation)),[])
        self.assertFalse(state.pdf_export_busy);self.assertNotIn('secret',state.pdf_export_message)
        State.request_consultation_pdf.fn(state);self.assertEqual(key,state._pdf_key)
        with self.locks(state),patch(TARGET,new_callable=AsyncMock,return_value=export_payload()) as request,patch('vet_tech.features.clinical.state.render_consultation_pdf',return_value=b'%PDF-synthetic'):
            events=await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
        self.assertEqual(len(events),1);self.assertIn('application/pdf',str(events[0]))
        self.assertEqual(request.await_args.kwargs['json_payload'],{'operacao':key})
        self.assertFalse(state.pdf_export_busy);self.assertEqual(state._pdf_key,'')

    async def test_failures_do_not_download_and_always_release_loading(self):
        for code in [401,403,404,400,409,429,500,None]:
            with self.subTest(code=code):
                state=self.prepare()
                with self.locks(state),patch(TARGET,new_callable=AsyncMock,side_effect=XanoRequestError('clinical-secret',status_code=code)):
                    events=await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
                self.assertFalse(any('download' in str(e.handler) for e in events));self.assertFalse(state.pdf_export_busy)
                self.assertNotIn('clinical-secret',state.pdf_export_message)

    async def test_missing_audit_or_renderer_failure_never_downloads(self):
        from test_consultation_pdf import export_payload
        for missing_audit in [True,False]:
            payload=export_payload()
            if missing_audit:payload.pop('auditoria_id')
            state=self.prepare()
            with self.locks(state),patch(TARGET,new_callable=AsyncMock,return_value=payload),patch('vet_tech.features.clinical.state.render_consultation_pdf',side_effect=RuntimeError('clinical-secret')) as renderer:
                events=await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
            self.assertFalse(any('download' in str(e.handler) for e in events));self.assertFalse(state.pdf_export_busy)
            self.assertNotIn('clinical-secret',state.pdf_export_message)
            if missing_audit:renderer.assert_not_called()

    async def test_late_http_response_cannot_restore_context_or_release_new_operation(self):
        from test_consultation_pdf import export_payload
        for change in ['pet','detail','logout','away-and-back']:
            with self.subTest(change=change):
                state=self.prepare();generation=state._pdf_generation
                started,release=asyncio.Event(),asyncio.Event()
                async def request(*args,**kwargs):
                    started.set();await release.wait();return export_payload()
                with self.locks(state),patch(TARGET,side_effect=request),patch('vet_tech.features.clinical.state.render_consultation_pdf') as renderer:
                    pending=asyncio.create_task(consume(State.generate_consultation_pdf.fn(state,generation)))
                    await started.wait()
                    if change=='pet':state._clear_pet_context()
                    elif change=='logout':state._expire_session()
                    else:
                        State.set_detail_id.fn(state,'')
                        if change=='away-and-back':
                            state.detail_id='42'
                            State.open_consultation_pdf.fn(state)
                            state.pdf_preview_loading = False
                            state.pdf_preview_ready = True
                            State.request_consultation_pdf.fn(state)
                    release.set();events=await pending
                self.assertEqual(events,[]);renderer.assert_not_called()
                if change=='away-and-back':self.assertTrue(state.pdf_export_busy)

    async def test_context_changes_during_render_do_not_download(self):
        import threading
        from test_consultation_pdf import export_payload
        state=self.prepare();started=threading.Event();release=threading.Event()
        def render(doc):
            started.set();release.wait(3);return b'%PDF-private'
        with self.locks(state),patch(TARGET,new_callable=AsyncMock,return_value=export_payload()),patch('vet_tech.features.clinical.state.render_consultation_pdf',side_effect=render):
            pending=asyncio.create_task(consume(State.generate_consultation_pdf.fn(state,state._pdf_generation)))
            await asyncio.to_thread(started.wait,2)
            State.set_detail_id.fn(state,'');release.set()
            self.assertEqual(await pending,[])

    async def test_renderer_timeout_and_ineligible_detail(self):
        import time
        from test_consultation_pdf import export_payload
        state=self.prepare()
        with self.locks(state),patch(TARGET,new_callable=AsyncMock,return_value=export_payload()),patch('vet_tech.features.clinical.state.RENDER_TIMEOUT_SECONDS',.001),patch('vet_tech.features.clinical.state.render_consultation_pdf',side_effect=lambda _:time.sleep(.03)):
            events=await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
        self.assertFalse(any('download' in str(e.handler) for e in events));self.assertFalse(state.pdf_export_busy)
        for status in ['legado','em_atendimento','agendada']:
            state._invalidate_pdf_export();state.detail={'status':status}
            self.assertIsNone(State.request_consultation_pdf.fn(state));self.assertFalse(state.pdf_export_busy)

    async def test_rollback_switch_blocks_export_without_changing_clinical_data(self):
        state=self.prepare();state._invalidate_pdf_export()
        before=deepcopy(state.detail)
        with patch.dict('os.environ',{'VET_TECH_CONSULTATION_PDF_ENABLED':'false'}),patch(TARGET,new_callable=AsyncMock) as request:
            self.assertIsNone(State.request_consultation_pdf.fn(state))
            self.assertFalse(state.pdf_export_busy);self.assertEqual(state.detail,before)
            request.assert_not_called()
