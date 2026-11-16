"""Contrato de cadastro Google: provas privadas e dados obrigatórios."""
import os
import unittest
from unittest.mock import AsyncMock, patch

from test_google_login import google_state, at_return, run, redirects, AUTHORIZE
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError

REQUEST = 'vet_tech.features.auth.state.xano_request'


class GoogleRegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_start_selects_signup_intent(self):
        state = google_state(signup_profile='veterinario')
        with patch.dict(os.environ, GOOGLE_LOGIN_ENABLED='true'), patch(REQUEST, new_callable=AsyncMock, return_value={'url': AUTHORIZE}) as request:
            await run(State.start_google_signup, state)
        self.assertEqual(request.await_args.args[2], 'acesso/google/inicio?intencao=cadastro')
        self.assertEqual(state._google_intent, 'cadastro')
        self.assertEqual(state.signup_profile, 'veterinario')

    async def test_callback_only_prefills_no_session(self):
        state = google_state(_google_intent='cadastro', _google_state='s')
        at_return(state, 'code=c&state=s')
        with patch(REQUEST, new_callable=AsyncMock, return_value={'resultado':'cadastro','prova':'secret','email':'name@example.invalid','nome':'Nome'}) as request:
            events = await run(State.finish_google_login, state)
        self.assertFalse(state.is_authenticated)
        self.assertTrue(state.google_signup)
        self.assertEqual(state._google_signup_proof, 'secret')
        self.assertEqual(redirects(events), ['/cadastro'])
        request.assert_awaited_once()

    async def test_login_intent_rejects_signup_proof(self):
        state = google_state(_google_state='s')
        at_return(state, 'code=c&state=s')
        with patch(REQUEST, new_callable=AsyncMock, return_value={'resultado':'cadastro','prova':'secret','email':'x@example.invalid'}):
            await run(State.finish_google_login, state)
        self.assertFalse(state.google_signup)
        self.assertFalse(state.is_authenticated)

    async def test_missing_fields_never_submit(self):
        state = google_state(google_signup=True, google_signup_email='name@example.invalid', _google_signup_proof='secret')
        with patch(REQUEST, new_callable=AsyncMock) as request:
            await run(State.signup, state, {'nome':'Nome','telefone':'11999999999','cpf':'52998224725'})
        request.assert_not_awaited()

    async def test_submission_uses_proof_without_email_or_password(self):
        state = google_state(google_signup=True, google_signup_email='verified@example.invalid', _google_signup_proof='secret')
        # Reject after capturing request to avoid constructing an authenticated fixture.
        with patch(REQUEST, new_callable=AsyncMock, side_effect=XanoRequestError('rejeitado')) as request:
            await run(State.signup, state, {'nome':'Nome','telefone':'11999999999','cpf':'52998224725','endereco':'Rua','email':'forged@example.invalid','password':'forged'})
        self.assertEqual(request.await_args.args[2], 'acesso/google/cadastro')
        payload=request.await_args.kwargs['json_payload']
        self.assertEqual(payload['prova'], 'secret')
        self.assertNotIn('email', payload)
        self.assertNotIn('password', payload)
        self.assertEqual(payload['perfil'], 'tutor')

    async def test_failed_session_confirmation_returns_to_login_without_retry(self):
        state=google_state(google_signup=True, google_signup_email='x@example.invalid', _google_signup_proof='p')
        with patch(REQUEST,new_callable=AsyncMock,side_effect=[{'resultado':'sessao','authToken':'t','perfil':'tutor','identidade_id':7},XanoRequestError('falha')]) as request:
            events=await run(State.signup,state,{'nome':'Nome','telefone':'11999999999','cpf':'52998224725','endereco':'Rua'})
        self.assertEqual(request.await_count,2)
        self.assertEqual(redirects(events),['/login'])
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._google_signup_proof,'')
        self.assertIn('Cadastro concluído',state.login_message)

    async def test_cancel_clears_proof(self):
        state=google_state(google_signup=True, _google_signup_proof='secret', google_signup_email='x@example.invalid')
        State.cancel_google_signup.fn(state)
        self.assertFalse(state.google_signup)
        self.assertEqual(state._google_signup_proof,'')
        self.assertEqual(state.google_signup_email,'')

class GooglePasswordSettingsTests(unittest.IsolatedAsyncioTestCase):
    def test_account_save_preserves_missing_password_flag(self):
        from vet_tech.features.settings.state import SettingsState
        from test_settings_state import ACCOUNT
        state=SettingsState(_reflex_internal_init=True)
        state._apply({**ACCOUNT,'possui_senha':False})
        self.assertFalse(state.has_local_password)
        state._apply(ACCOUNT)
        self.assertFalse(state.has_local_password)

    async def test_first_password_clears_session_before_recovery(self):
        from vet_tech.features.settings.state import SettingsState
        from test_settings_state import ACCOUNT
        auth=google_state(is_authenticated=True, _auth_token='session', profile='tutor', identity_id='7')
        settings=SettingsState(_reflex_internal_init=True)
        settings._session=auth._auth_token
        settings._context=settings._context_for(auth)
        settings._apply({**ACCOUNT,'possui_senha':False})
        with patch.object(SettingsState,'get_state',AsyncMock(return_value=auth)):
            events=[e async for e in SettingsState.define_first_password.fn(settings)]
        self.assertFalse(auth.is_authenticated)
        self.assertEqual(auth.recovery_step,'email')
        self.assertEqual(redirects(events),['/login'])
