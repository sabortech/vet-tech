"""Own-account metadata loading must release the lock and reject stale sessions."""
import asyncio
import unittest
from unittest.mock import AsyncMock,patch
from test_clinical_state import session
from test_pet_clinical_loading import state_lock
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError
TARGET='vet_tech.features.auth.state.xano_request'

class VeterinarianIdentityTests(unittest.IsolatedAsyncioTestCase):
    async def test_account_metadata_is_authenticated_cached_and_outside_lock(self):
        state=session('veterinario');state.identity_name='Dra. Fernanda Diniz'
        with state_lock(state) as held:
            async def request(*args,**kwargs):
                self.assertFalse(held[0]);self.assertEqual(args[2],'veterinario/account')
                self.assertEqual(kwargs['auth_token'],'synthetic-session')
                return {'crmv':'12345','crmv_uf':'sp'}
            with patch(TARGET,side_effect=request) as call:
                await State.load_professional_identity.fn(state)
                await State.load_professional_identity.fn(state)
        self.assertEqual(call.await_count,1)
        self.assertEqual(state.veterinarian_registration,'CRMV 12345 / SP')
        self.assertEqual(state.veterinarian_initials,'FD')
        state._clear_session()
        self.assertEqual(state.identity_crmv,'');self.assertFalse(state.identity_professional_loaded)

    async def test_tutor_never_reads_medical_account(self):
        state=session('tutor')
        with state_lock(state),patch(TARGET,AsyncMock()) as call:
            await State.load_professional_identity.fn(state)
        call.assert_not_called()

    async def test_absent_registration_is_not_invented(self):
        state=session('veterinario')
        with state_lock(state),patch(TARGET,AsyncMock(return_value={'crmv':'','crmv_uf':''})):
            await State.load_professional_identity.fn(state)
        self.assertEqual(state.veterinarian_registration,'CRMV não informado')

    async def test_failure_can_retry_without_blocking_session(self):
        state=session('veterinario')
        with state_lock(state),patch(TARGET,AsyncMock(side_effect=[XanoRequestError('Erro',status_code=500),{'crmv':'77','crmv_uf':'RJ'}])):
            await State.load_professional_identity.fn(state)
            self.assertEqual(state.veterinarian_registration,'Registro indisponível')
            self.assertFalse(state.identity_professional_loading)
            await State.load_professional_identity.fn(state)
        self.assertEqual(state.veterinarian_registration,'CRMV 77 / RJ')

    async def test_old_response_cannot_populate_new_session(self):
        for dimension,new in [('_session_generation',99),('_auth_token','new-token'),('identity_id','99'),('profile','tutor')]:
            with self.subTest(dimension=dimension):
                state=session('veterinario')
                async def request(*args,**kwargs):
                    setattr(state,dimension,new)
                    return {'crmv':'private-old','crmv_uf':'SP'}
                with state_lock(state),patch(TARGET,side_effect=request):
                    await State.load_professional_identity.fn(state)
                self.assertEqual(state.identity_crmv,'')
                self.assertFalse(state.identity_professional_loaded)

    async def test_expired_token_clears_metadata(self):
        for status,message in ((401,'Expirou'),(403,'Sessão inválida.')):
            with self.subTest(status=status):
                state=session('veterinario')
                with state_lock(state),patch(TARGET,AsyncMock(side_effect=XanoRequestError(message,status_code=status))):
                    await State.load_professional_identity.fn(state)
                self.assertFalse(state.is_authenticated)
                self.assertFalse(state.identity_professional_loading)
