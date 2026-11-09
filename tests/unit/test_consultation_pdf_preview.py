"""State-level authorization, isolation and request budget for the shared panel."""
import asyncio
from copy import deepcopy
import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state
import test_clinical_state as clinical_tests
from test_clinical_state import consume, TARGET
from test_consultation_pdf import export_payload
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError


class PDFPreviewTests(unittest.IsolatedAsyncioTestCase):
    def prepare(self, profile='tutor', agenda=False):
        state=make_state();state.profile=profile;state.is_authenticated=True;state._auth_token='synthetic-only'
        state.selected_pet={'id':'7'};state.active_section='Consultas'
        state.detail_id='42';state.detail={'id':'42','status':'finalizada'}
        state.clinical_pet_id='7';state.clinical_id='42';state.clinical_status='finalizada'
        if agenda:
            state.agenda_rows=[{'id':'42','pet_id':'7','status':'finalizada','autorizado':'sim'}]
            State.open_agenda_consultation_pdf.fn(state,'7','42')
        else:
            State.open_consultation_pdf.fn(state)
        return state

    def locks(self, state):
        return clinical_tests.ConsultationPDFStateTests.locks(self,state)

    async def load(self,state,payload=None):
        with self.locks(state),patch(TARGET,AsyncMock(return_value=payload or export_payload())) as request:
            await consume(State.load_consultation_pdf_preview.fn(state,state._pdf_generation))
        return request

    async def test_all_origins_use_one_read_and_only_confirmation_downloads(self):
        for profile,agenda in [('tutor',False),('veterinario',False),('veterinario',True)]:
            with self.subTest(profile=profile,agenda=agenda):
                state=self.prepare(profile,agenda)
                self.assertTrue(state.pdf_preview_open)
                self.assertIsNone(State.request_consultation_pdf.fn(state))
                request=await self.load(state)
                request.assert_awaited_once()
                self.assertEqual(request.await_args.args[:2],('GET','vettech-clinical'))
                self.assertEqual(request.await_args.args[2],f'{profile}/pets/7/consultas/42/previa-pdf')
                self.assertTrue(state.pdf_preview_ready)
                self.assertIn('Amora',state.pdf_preview_title)
                # Reopen while already displayed must not fetch or clear data.
                generation=state._pdf_generation
                event=State.open_agenda_consultation_pdf.fn(state,'7','42') if agenda else State.open_consultation_pdf.fn(state)
                self.assertIsNone(event);self.assertEqual(state._pdf_generation,generation)
                State.request_consultation_pdf.fn(state)
                self.assertIsNone(State.request_consultation_pdf.fn(state))
                with self.locks(state),patch(TARGET,AsyncMock(return_value=export_payload())) as request,patch('vet_tech.features.clinical.state.render_consultation_pdf',return_value=b'%PDF-synthetic') as renderer:
                    events=await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
                self.assertEqual(len(events),1)
                request.assert_awaited_once();renderer.assert_not_called()
                self.assertEqual(request.await_args.args[2],f'{profile}/pets/7/consultas/42/exportar')

    async def test_cancel_and_close_do_not_request_or_keep_sensitive_preview(self):
        state=self.prepare();await self.load(state)
        with patch(TARGET,AsyncMock()) as request:
            State.change_pdf_preview_open.fn(state,False)
            self.assertIsNone(State.request_consultation_pdf.fn(state))
        request.assert_not_awaited()
        self.assertFalse(state.pdf_preview_open);self.assertEqual(state.pdf_preview_fields,[])
        self.assertEqual(state._pdf_signature,'')

    async def test_changed_document_requires_reconfirmation_without_extra_get(self):
        state=self.prepare();await self.load(state)
        changed=export_payload();changed['consulta']['obs']='Informação atualizada'
        State.request_consultation_pdf.fn(state)
        with self.locks(state),patch(TARGET,AsyncMock(return_value=changed)) as request,patch('vet_tech.features.clinical.state.render_consultation_pdf',return_value=b'%PDF-updated') as renderer:
            events=await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
        self.assertEqual(len(events),1);self.assertIn('call_script',str(events));renderer.assert_called_once();request.assert_awaited_once()
        self.assertIn('novamente',state.pdf_export_message)
        self.assertEqual(state._pdf_preview_bytes,b'%PDF-updated')
        self.assertFalse(state.pdf_export_busy)

    async def test_preview_failure_retry_and_revocation_clear_data(self):
        state=self.prepare('veterinario')
        with self.locks(state),patch(TARGET,AsyncMock(side_effect=XanoRequestError('private',status_code=500))):
            await consume(State.load_consultation_pdf_preview.fn(state,state._pdf_generation))
        self.assertFalse(state.pdf_preview_loading);self.assertFalse(state.pdf_preview_ready)
        self.assertNotIn('private',state.pdf_export_message)
        self.assertIsNotNone(State.retry_pdf_preview.fn(state))
        self.assertIsNone(State.retry_pdf_preview.fn(state))
        await self.load(state)
        State.request_consultation_pdf.fn(state)
        with self.locks(state),patch(TARGET,AsyncMock(side_effect=XanoRequestError('secret',status_code=403))):
            await consume(State.generate_consultation_pdf.fn(state,state._pdf_generation))
        self.assertFalse(state.pdf_preview_ready);self.assertEqual(state.pdf_preview_fields,[])
        self.assertEqual(state.pdf_preview_sections,[])

    async def test_late_preview_is_discarded_for_every_context_change(self):
        for change in ('close','logout','pet','consultation','profile','route'):
            with self.subTest(change=change):
                state=self.prepare();started=asyncio.Event();release=asyncio.Event()
                async def request(*a,**kw):
                    started.set();await release.wait();return export_payload()
                with self.locks(state),patch(TARGET,side_effect=request):
                    task=asyncio.create_task(consume(State.load_consultation_pdf_preview.fn(state,state._pdf_generation)))
                    await started.wait()
                    if change=='close':State.change_pdf_preview_open.fn(state,False)
                    elif change=='logout':state._expire_session()
                    elif change=='pet':state.selected_pet={'id':'8'}
                    elif change=='consultation':State.set_detail_id.fn(state,'43')
                    elif change=='profile':state.profile='veterinario'
                    else:state.router.url.path='/other'
                    release.set();await task
                self.assertFalse(state.pdf_preview_ready)
                self.assertEqual(state.pdf_preview_fields,[])

    async def test_sessions_and_full_complements_are_isolated(self):
        a=self.prepare();b=self.prepare('veterinario')
        payload=export_payload();payload['exames']=[{'id':1,'pet_id':7,'consulta_id':42,'tipo':'Hemograma','resultado':'ç ã é\nLinha 2'}]
        await self.load(a,payload)
        self.assertTrue(a._pdf_preview_bytes.startswith(b'%PDF-'))
        self.assertEqual(a.pdf_preview_sections,[])
        self.assertEqual(b.pdf_preview_sections,[])
        self.assertFalse(b.pdf_preview_ready)
        State.change_pdf_preview_open.fn(a,False)
        self.assertTrue(b.pdf_preview_open)

    def test_ineligible_origins_make_no_request(self):
        state=self.prepare();State.change_pdf_preview_open.fn(state,False)
        for status in ('agendada','em_atendimento','legado','cancelada',''):
            state.detail={'status':status}
            self.assertIsNone(State.open_consultation_pdf.fn(state))
        state.profile='veterinario';state.agenda_rows=[{'id':'42','pet_id':'7','status':'finalizada','autorizado':'nao'}]
        self.assertIsNone(State.open_agenda_consultation_pdf.fn(state,'7','42'))

    async def test_completed_consultations_use_the_current_list_without_loading_agenda(self):
        state=self.prepare('veterinario',True)
        State.change_pdf_preview_open.fn(state,False)
        state.vet_section='Consultas';state.upcoming_rows=deepcopy(state.agenda_rows);state.agenda_rows=[]
        self.assertIsNotNone(State.open_agenda_consultation_pdf.fn(state,'7','42'))
        request=await self.load(state)
        request.assert_awaited_once()
        self.assertTrue(state.pdf_preview_ready)

    async def test_reopened_finalized_attendance_does_not_load_editing_catalog(self):
        from reflex.istate.data import RouterData, PageData
        state=self.prepare('veterinario')
        state.router=RouterData(_page=PageData(params={'consulta_id':'42'}))
        row={'id':42,'pet_id':7,'status':'finalizada','versao':2,'rascunho':{}}
        with patch(TARGET,AsyncMock(return_value={'consulta':row,'pet':{'id':7,'nome':'Amora'}})) as request:
            await consume(State.load_attendance.fn(state))
        request.assert_awaited_once()
        self.assertTrue(request.await_args.args[2].endswith('/rascunho'))
        self.assertEqual(state.disease_options,[])
