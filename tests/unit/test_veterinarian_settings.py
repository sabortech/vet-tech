import unittest
from unittest.mock import AsyncMock, patch

from reflex.istate.data import ReflexURL, RouterData
from test_settings_state import consume, SettingsTests
from vet_tech.features.auth.state import State
from vet_tech.features.settings.state import SettingsState
from vet_tech.shared.xano_client import XanoRequestError

TARGET = 'vet_tech.features.settings.state.xano_request'
ACCOUNT = {'nome': 'Veterinária sintética', 'email': 'vet@example.invalid', 'telefone': '11999999999', 'crmv': '12345', 'crmv_uf': 'SP'}


def make():
    state, auth = SettingsTests().make()
    state.clear()
    auth.profile, auth.identity_id = 'veterinario', '7'
    state.account_profile = auth.profile
    state._session = auth._auth_token
    state._context = state._context_for(auth)
    state._apply(ACCOUNT)
    return state, auth


class VeterinarianSettingsTests(unittest.IsolatedAsyncioTestCase):
    async def test_load_uses_vet_endpoint_and_clears_tutor_fields(self):
        state, auth = make()
        state.endereco, state.cpf_mascarado = 'stale', 'stale'
        state.loading = True
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch.object(SettingsState, '__aenter__', AsyncMock(return_value=state)), patch.object(SettingsState, '__aexit__', AsyncMock(return_value=False)), patch(TARGET, AsyncMock(return_value=ACCOUNT)) as request:
            await consume(SettingsState.load_account.fn(state))
        self.assertEqual(request.await_args.args[2], 'veterinario/account')
        self.assertEqual(state.crmv_label, '12345 / SP')
        self.assertEqual((state.endereco, state.cpf_mascarado), ('', ''))
        self.assertTrue(state.loaded)

    async def test_save_only_name_phone_and_updates_sidebar_identity(self):
        state, auth = make()
        state.nome = ' Novo nome '
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch(TARGET, AsyncMock(return_value={**ACCOUNT, 'nome': 'Novo nome'})) as request:
            await consume(SettingsState.save.fn(state, {'email': 'forged', 'crmv': 'forged', 'id': 55, 'endereco': 'forged'}))
        self.assertEqual(request.await_args.args[2], 'veterinario/account')
        self.assertEqual(request.await_args.kwargs['json_payload'], {'nome': 'Novo nome', 'telefone': ACCOUNT['telefone']})
        self.assertEqual(auth.identity_name, 'Novo nome')
        self.assertFalse(state.dirty)
        self.assertEqual(state.crmv, ACCOUNT['crmv'])

    async def test_blank_field_and_duplicate_save_do_not_write(self):
        state, auth = make()
        state.telefone = ' '
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch(TARGET, AsyncMock()) as request:
            await consume(SettingsState.save.fn(state, {}))
            state.telefone = 'new'
            state.saving = True
            await consume(SettingsState.save.fn(state, {}))
        request.assert_not_awaited()
        self.assertTrue(state.message)

    async def test_password_uses_vet_endpoint_without_trimming_and_keeps_wrong_current(self):
        state, auth = make()
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch(TARGET, AsyncMock(side_effect=XanoRequestError('Senha atual incorreta.', 400))) as request:
            await consume(SettingsState.change_password.fn(state, {'current_password': ' old ', 'new_password': ' new ', 'password_confirmation': ' new '}))
        self.assertEqual(request.await_args.args[2], 'veterinario/password')
        self.assertEqual(request.await_args.kwargs['json_payload']['new_password'], ' new ')
        self.assertTrue(auth.is_authenticated)
        self.assertFalse(state.saving)

    async def test_password_success_cleans_veterinarian_session(self):
        state, auth = make()
        async def get_state(instance, cls):
            return state if cls is SettingsState else auth
        with patch.object(SettingsState, 'get_state', get_state), patch.object(State, 'get_state', get_state), patch(TARGET, AsyncMock(return_value={'success': True})):
            await consume(SettingsState.change_password.fn(state, {'current_password': 'old', 'new_password': 'new', 'password_confirmation': 'new'}))
        self.assertFalse(auth.is_authenticated)
        self.assertEqual(state.account_profile, '')
        self.assertEqual(state.crmv, '')
        self.assertIn('Senha atualizada', auth.login_message)

    async def test_same_token_different_profile_or_generation_cannot_restore_old_load(self):
        for dimension in ('profile', '_session_generation', 'identity_id'):
            with self.subTest(dimension=dimension):
                state, auth = make()
                state.loading = True
                async def response(*args, **kwargs):
                    setattr(auth, dimension, {'profile': 'tutor', '_session_generation': auth._session_generation + 1, 'identity_id': '99'}[dimension])
                    state.clear()
                    state.message = 'new-session'
                    return ACCOUNT
                with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)), patch.object(SettingsState, '__aenter__', AsyncMock(return_value=state)), patch.object(SettingsState, '__aexit__', AsyncMock(return_value=False)), patch(TARGET, AsyncMock(side_effect=response)):
                    await consume(SettingsState.load_account.fn(state))
                self.assertFalse(state.loaded)
                self.assertEqual(state.email, '')
                self.assertEqual(state.message, 'new-session')

    def test_menu_guard_allows_only_vet_routes_and_keeps_exact_intent(self):
        state, _ = make()
        state.nome = 'Rascunho'
        state.request_navigation('/dashboard')
        self.assertFalse(state.discard_open)
        state.request_navigation('/?secao=consultas')
        self.assertTrue(state.discard_open)
        self.assertEqual(state._pending, '/?secao=consultas')
        state.keep_editing()
        self.assertEqual(state.nome, 'Rascunho')
        state.request_navigation('/?secao=horarios')
        state.discard()
        self.assertEqual(state.nome, ACCOUNT['nome'])
        self.assertFalse(state.dirty)

    async def test_enter_switches_role_context_even_when_token_is_reused(self):
        state, auth = SettingsTests().make()
        auth.profile, auth.identity_id = 'veterinario', '7'
        with patch.object(SettingsState, 'get_state', AsyncMock(return_value=auth)):
            events = await consume(SettingsState.enter.fn(state))
        self.assertTrue(events)
        self.assertEqual(state.account_profile, 'veterinario')
        self.assertEqual(state.cpf_mascarado, '')
        self.assertFalse(state.loaded)
        self.assertTrue(state.loading)

    async def test_return_link_selects_correct_agenda_section(self):
        from test_clinical_state import session
        auth = session("veterinario")
        auth.router = RouterData(url=ReflexURL('http://localhost/?secao=consultas'))
        with patch('vet_tech.features.clinical.state.xano_request', AsyncMock(return_value={'items': [], 'total': 0})) as request:
            await consume(State.enter_veterinary_agenda.fn(auth))
        self.assertEqual(auth.vet_section, 'Consultas')
        self.assertNotIn('dia=', request.await_args.args[2])
