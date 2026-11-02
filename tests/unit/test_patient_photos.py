"""Authorized patient photos: explicit null is distinct from missing contracts."""
import asyncio
import unittest
from reflex.istate.data import RouterData, PageData
from unittest.mock import AsyncMock, patch
from test_clinical_state import session, consume, TARGET
from test_clinical_projections import execute
from vet_tech.features.auth.state import State
from vet_tech.features.clinical.state import patient_photo, pet_summary

PHOTO = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='

class PatientPhotoTests(unittest.IsolatedAsyncioTestCase):
    def test_null_overrides_old_photo_and_missing_contract_is_not_null(self):
        rows = [{'pet_id':'1','autorizado':'sim','pet_foto':PHOTO}]
        for value in (None, ''):
            self.assertEqual(patient_photo({'foto':value},'1',rows), {'foto':'','foto_ausente':'sim'})
        self.assertEqual(patient_photo({},'1',rows)['foto'], PHOTO)
        self.assertEqual(patient_photo({},'2',rows), {'foto':'','foto_ausente':'nao'})
        self.assertEqual(patient_photo({'foto':'javascript:alert(1)'},'1',rows), {'foto':'','foto_ausente':'nao'})
        self.assertEqual(pet_summary({'foto':PHOTO})['foto'],PHOTO)

    async def test_history_explicit_null_cannot_restore_cached_photo(self):
        state=session('veterinario')
        state.agenda_rows=[{'pet_id':'1','autorizado':'sim','pet_foto':PHOTO}]
        with patch(TARGET,AsyncMock(return_value={'pet':{'foto':None},'historico':{}})):
            await State.open_prior_history.fn(state,'1')
        self.assertEqual(state.prior_pet_info['foto'],'')
        self.assertEqual(state.prior_pet_info['foto_ausente'],'sim')

    async def test_summary_prefers_current_base64_and_respects_null(self):
        state=session('veterinario'); state.vet_section='Consultas'
        state.upcoming_rows=[{'id':'7','pet_id':'1','autorizado':'sim','pet_foto':'https://example.invalid/old.jpg'}]
        for value in (PHOTO, None):
            with patch(TARGET,AsyncMock(return_value={'pet':{'nome':'Synthetic','foto':value},'historico':{}})):
                await consume(State.select_consultation.fn(state,'7'))
            self.assertEqual(state.consultation_info['foto'],value or '')
            self.assertEqual(state.consultation_info['foto_ausente'],'sim' if value is None else 'nao')

    async def test_attendance_uses_response_photo_and_null_even_with_cache(self):
        state=session('veterinario')
        state.router = RouterData(_page=PageData(params={'consulta_id':'7'}))
        state.agenda_rows=[{'pet_id':'1','autorizado':'sim','pet_foto':'https://example.invalid/old.jpg'}]
        for value in (PHOTO, None):
            data={'pet':{'nome':'Synthetic','foto':value},'consulta':{'id':7,'pet_id':1,'status':'em_atendimento','versao':1}}
            with patch(TARGET,AsyncMock(side_effect=[data,[]])):
                await consume(State.load_attendance.fn(state))
            self.assertEqual(state.clinical_pet_info['foto'],value or '')
            self.assertEqual(state.clinical_pet_info['foto_ausente'],'sim' if value is None else 'nao')

    async def test_stale_attendance_photo_is_discarded(self):
        state=session('veterinario'); state.router = RouterData(_page=PageData(params={'consulta_id':'7'}))
        started,release=asyncio.Event(),asyncio.Event()
        async def request(*args,**kwargs):
            started.set(); await release.wait()
            return {'pet':{'nome':'Synthetic','foto':PHOTO},'consulta':{'id':7,'pet_id':1,'status':'em_atendimento','versao':1}}
        with patch(TARGET,side_effect=request):
            pending=asyncio.create_task(consume(State.load_attendance.fn(state)))
            await started.wait(); state._clear_clinical_session(); release.set(); await pending
        self.assertEqual(state.clinical_pet_info,{})

    async def test_agenda_preserves_base64_null_and_revocation(self):
        state=session('veterinario')
        rows=[{'id':i,'pet_id':i,'pet_foto':value,'autorizado':allowed,'agendada_para':1893544200000,'status':'agendada'}
              for i,(value,allowed) in enumerate([(PHOTO,True),(None,True),(PHOTO,False)],1)]
        with patch(TARGET,AsyncMock(return_value={'items':rows,'total':3})):
            await consume(State.load_agenda.fn(state))
        self.assertEqual(state.agenda_rows[0]['pet_foto'],PHOTO)
        self.assertEqual(state.agenda_rows[1]['foto_ausente'],'sim')
        self.assertEqual(state.agenda_rows[2]['pet_foto'],'')
        self.assertEqual(state.agenda_rows[2]['foto_ausente'],'nao')

    def test_backend_null_is_not_stringified(self):
        variables={'reservations':[{'id':1,'pet_id':5,'status':'agendada','agendada_para':1893544200000}],
                   'consents':[{'pet_id':5}], 'pets':[{'id':5,'nome':'Synthetic','foto':None}]}
        self.assertIsNone(execute('xano/api/clinical/agenda_GET.xs',{'page':1},variables)['items'][0]['pet_foto'])
