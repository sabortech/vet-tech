"""Portraits are exposed only after current authorized history succeeds."""
import unittest
from unittest.mock import AsyncMock,patch
from test_clinical_state import session,TARGET
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError

class HistoryPortraitTests(unittest.IsolatedAsyncioTestCase):
    async def test_response_photo_is_preferred_over_cached_photo(self):
        state=session('veterinario')
        state.agenda_rows=[{'pet_id':'1','autorizado':'sim','pet_foto':'https://example.invalid/old.png'}]
        with patch(TARGET,AsyncMock(return_value={'pet':{'nome':'Jessy','foto':'data:image/png;base64,c3ludGhldGlj'},'historico':{'consultas':[]}})):
            await State.open_prior_history.fn(state,'1')
        self.assertEqual(state.prior_pet_info['foto'],'data:image/png;base64,c3ludGhldGlj')

    async def test_old_contract_uses_only_same_pet_authorized_cached_photo(self):
        state=session('veterinario')
        state.agenda_rows=[{'pet_id':'2','autorizado':'sim','pet_foto':'https://example.invalid/other.png'},
                           {'pet_id':'1','autorizado':'nao','pet_foto':'https://example.invalid/revoked.png'}]
        response={'pet':{'nome':'Jessy'},'historico':{'consultas':[]}}
        with patch(TARGET,AsyncMock(return_value=response)):
            await State.open_prior_history.fn(state,'1')
            self.assertEqual(state.prior_pet_info['foto'],'')
            state.upcoming_rows=[{'pet_id':'1','autorizado':'sim','pet_foto':'https://example.invalid/current.png'}]
            await State.open_prior_history.fn(state,'1')
            self.assertEqual(state.prior_pet_info['foto'],'https://example.invalid/current.png')

    async def test_uri_is_sanitized_and_denial_never_reuses_cached_photo(self):
        state=session('veterinario')
        with patch(TARGET,AsyncMock(return_value={'pet':{'nome':'Jessy','foto':'javascript:alert(1)'},'historico':{'consultas':[]}})):
            await State.open_prior_history.fn(state,'1')
        self.assertEqual(state.prior_pet_info['foto'],'')
        state.agenda_rows=[{'pet_id':'1','autorizado':'sim','pet_foto':'https://example.invalid/authorized-before.png'}]
        with patch(TARGET,AsyncMock(side_effect=XanoRequestError('Revogado',status_code=403))):
            await State.open_prior_history.fn(state,'1')
        self.assertEqual(state.prior_pet_info,{})
