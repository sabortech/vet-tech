import unittest
from unittest.mock import AsyncMock, patch

from vet_tech.features.auth.state import State as AuthState
from vet_tech.features.settings.state import SettingsState
from vet_tech.shared.xano_client import XanoRequestError

ACCOUNT = {"nome": "Tutor A", "email": "a@example.invalid", "cpf_mascarado": "***.456.789-**", "telefone": "11999999999", "endereco": "Rua A"}


async def consume(events):
    return [event async for event in events]


class SettingsTests(unittest.IsolatedAsyncioTestCase):
    def make(self):
        auth = AuthState(_reflex_internal_init=True)
        auth._auth_token = "session-a"
        auth.is_authenticated = True
        auth.profile = "tutor"
        state = SettingsState(_reflex_internal_init=True)
        state._session = auth._auth_token
        state.account_profile = "tutor"
        state._context = state._context_for(auth)
        state._apply(ACCOUNT)
        return state, auth

    async def test_load_publishes_progress_and_discards_old_session_result(self):
        state, auth = self.make()
        state.clear()
        async def response(*args, **kwargs):
            auth._auth_token = 'session-b'
            return ACCOUNT
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch('vet_tech.features.settings.state.xano_request', AsyncMock(side_effect=response)) as call, patch.object(SettingsState,'__aenter__',AsyncMock(return_value=state)), patch.object(SettingsState,'__aexit__',AsyncMock(return_value=False)):
            events = await consume(SettingsState.enter.fn(state))
            self.assertTrue(state.loading)
            self.assertFalse(state.loaded)
            call.assert_not_awaited()
            self.assertEqual(len(events),2)
            await consume(SettingsState.load_account.fn(state))
        self.assertFalse(state.loaded)
        self.assertEqual(state.email, '')

    async def test_same_session_cache_avoids_reload_but_expiration_schedules_background(self):
        state, auth = self.make()
        with patch.object(SettingsState,'get_state',AsyncMock(return_value=auth)), patch('vet_tech.features.settings.state.xano_request',AsyncMock()) as call:
            self.assertEqual(await consume(SettingsState.enter.fn(state)),[])
            state._loaded_at -= 61
            self.assertEqual(len(await consume(SettingsState.enter.fn(state))),2)
            self.assertTrue(state.loading)
            call.assert_not_awaited()

    async def test_background_load_releases_lock_during_network_and_handles_failure(self):
        state, auth = self.make()
        state.loading = True
        locked = False
        async def enter(*args):
            nonlocal locked
            locked=True
            return state
        async def leave(*args):
            nonlocal locked
            locked=False
        async def response(*args,**kwargs):
            self.assertFalse(locked)
            raise XanoRequestError('Falha de rede')
        with patch.object(SettingsState,'get_state',AsyncMock(return_value=auth)), patch.object(SettingsState,'__aenter__',enter), patch.object(SettingsState,'__aexit__',leave), patch('vet_tech.features.settings.state.xano_request',AsyncMock(side_effect=response)):
            await consume(SettingsState.load_account.fn(state))
        self.assertFalse(state.loading)
        self.assertEqual(state.message,'Falha de rede')
        self.assertTrue(state.loaded)

    async def test_save_uses_allowlist_and_snapshot_and_busy_guard(self):
        state, auth = self.make()
        state.nome = '  Atualizado  '
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch('vet_tech.features.settings.state.xano_request', AsyncMock(return_value={**ACCOUNT,'nome':'Atualizado'})) as call:
            events = SettingsState.save.fn(state, {'id':999, 'email':'forged'})
            await anext(events)
            self.assertTrue(state.saving)
            call.assert_not_awaited()
            await consume(SettingsState.save.fn(state, {}))
            await consume(events)
        self.assertEqual(call.await_args.kwargs['json_payload'], {'nome':'Atualizado','telefone':ACCOUNT['telefone'],'endereco':ACCOUNT['endereco']})
        self.assertFalse(state.dirty)
        self.assertTrue(state.message_ok)

    async def test_failed_save_retains_draft_and_no_false_success(self):
        state, auth = self.make()
        state.nome = 'Rascunho'
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch('vet_tech.features.settings.state.xano_request', AsyncMock(side_effect=XanoRequestError('Falha'))):
            await consume(SettingsState.save.fn(state, {}))
        self.assertEqual(state.nome,'Rascunho')
        self.assertTrue(state.dirty)
        self.assertFalse(state.saving)
        self.assertFalse(state.message_ok)
        state.cancel()
        self.assertEqual(state.nome,ACCOUNT['nome'])

    async def test_password_mismatch_blocks_api_and_wrong_current_keeps_session(self):
        state, auth = self.make()
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch('vet_tech.features.settings.state.xano_request', AsyncMock(side_effect=XanoRequestError('Senha atual incorreta.',400))) as call:
            await consume(SettingsState.change_password.fn(state, {'current_password':'wrong','new_password':'x','password_confirmation':'y'}))
            call.assert_not_awaited()
            await consume(SettingsState.change_password.fn(state, {'current_password':'wrong','new_password':' x ','password_confirmation':' x '}))
        self.assertEqual(call.await_args.kwargs['json_payload']['new_password'], ' x ')
        self.assertTrue(auth.is_authenticated)
        self.assertEqual(state.message,'Senha atual incorreta.')
        self.assertFalse(state.saving)

    async def test_password_success_cleans_session_and_redirects(self):
        state, auth = self.make()
        async def get_state(instance, cls):
            return state if cls is SettingsState else auth
        with patch.object(SettingsState,'get_state',get_state), patch.object(AuthState,'get_state',get_state), patch('vet_tech.features.settings.state.xano_request', AsyncMock(return_value={'success':True})):
            result = await consume(SettingsState.change_password.fn(state, {'current_password':'old','new_password':'new','password_confirmation':'new'}))
        self.assertFalse(auth.is_authenticated)
        self.assertEqual(auth._auth_token,'')
        self.assertEqual(state.email,'')
        self.assertIn('Senha atualizada',auth.login_message)
        self.assertTrue(result)

    def test_discard_guard_and_clean_navigation(self):
        state, _ = self.make()
        state.nome = 'Rascunho'
        self.assertIsNone(state.request_action('security'))
        self.assertTrue(state.discard_open)
        self.assertEqual(state.tab,'account')
        state.keep_editing()
        self.assertEqual(state.nome,'Rascunho')
        state.request_action('security')
        state.discard()
        self.assertEqual(state.tab,'security')
        self.assertFalse(state.dirty)
        self.assertEqual(state.nome,ACCOUNT['nome'])

    async def test_unauthenticated_entry_redirects_without_api(self):
        state, auth = self.make()
        auth._auth_token = ""
        auth.is_authenticated = False
        with patch.object(SettingsState,'get_state',AsyncMock(return_value=auth)), patch('vet_tech.features.settings.state.xano_request',AsyncMock()) as call:
            events = await consume(SettingsState.enter.fn(state))
        call.assert_not_awaited()
        self.assertTrue(events)
        self.assertFalse(state.loaded)
        self.assertEqual(state.email, "")

    def test_history_guard_honors_live_browser_edit_before_state_delta(self):
        state, _ = self.make()
        self.assertFalse(state.dirty)
        state.history_back()
        self.assertTrue(state.discard_open)
        self.assertEqual(state._pending, "history")

    def test_error_classification_preserves_domain_rejection(self):
        self.assertTrue(XanoRequestError('Falha',401).session_invalid)
        self.assertTrue(XanoRequestError('Sessão inválida.',403).session_invalid)
        self.assertFalse(XanoRequestError('Senha atual incorreta.',400).session_invalid)
        self.assertFalse(XanoRequestError('Negado',403).session_invalid)
