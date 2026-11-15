import os
import unittest
from unittest.mock import AsyncMock, patch

from reflex.istate.data import ReflexURL, RouterData

from test_auth_state import make_state
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import (
    GOOGLE_LOGIN_FAILED,
    GOOGLE_LOGIN_NO_ACCOUNT,
    XanoRequestError,
)

REQUEST = "vet_tech.features.auth.state.xano_request"
AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth?client_id=c&state=estado-da-aba&code_challenge=x"
TUTOR_SESSION = {"resultado": "sessao", "authToken": "google-token", "perfil": "tutor", "identidade_id": 7}
VET_SESSION = {"resultado": "sessao", "authToken": "google-token", "perfil": "veterinario", "identidade_id": 9}


def google_state(**overrides):
    state = make_state()
    state._google_state = ""
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


def at_return(state, query):
    state.router = RouterData(url=ReflexURL("http://localhost:3000/login/google?" + query))


def redirects(events):
    paths = []
    for event in events:
        for item in event if isinstance(event, list) else [event]:
            args = dict((name._js_expr, value._var_value) for name, value in getattr(item, "args", ()) or ())
            if "path" in args:
                paths.append(args["path"])
    return paths


async def run(handler, state, *args):
    return [event async for event in handler.fn(state, *args)]


class GoogleLoginStartTests(unittest.IsolatedAsyncioTestCase):
    async def test_disabled_flag_makes_no_request(self):
        state = google_state()
        with patch.dict(os.environ, {"GOOGLE_LOGIN_ENABLED": "false"}), \
                patch(REQUEST, new_callable=AsyncMock) as request:
            events = await run(State.start_google_login, state)
        request.assert_not_awaited()
        self.assertEqual(events, [])
        self.assertEqual(state._google_state, "")

    async def test_start_keeps_state_in_tab_and_redirects_to_google(self):
        state = google_state(_auth_token="sessao-anterior", is_authenticated=True)
        with patch.dict(os.environ, {"GOOGLE_LOGIN_ENABLED": "true"}), \
                patch(REQUEST, new_callable=AsyncMock, return_value={"url": AUTHORIZE}) as request:
            events = await run(State.start_google_login, state)
        request.assert_awaited_once()
        self.assertEqual(request.await_args.args[2], "acesso/google/inicio")
        self.assertEqual(state._google_state, "estado-da-aba")
        self.assertEqual(redirects(events), [AUTHORIZE])
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertFalse(state.is_busy)

    async def test_start_rejects_url_outside_google(self):
        state = google_state()
        with patch.dict(os.environ, {"GOOGLE_LOGIN_ENABLED": "true"}), \
                patch(REQUEST, new_callable=AsyncMock, return_value={"url": "https://evil.example/?state=x"}):
            events = await run(State.start_google_login, state)
        self.assertEqual(redirects(events), [])
        self.assertEqual(state._google_state, "")
        self.assertTrue(state.login_message)
        self.assertFalse(state.is_busy)


class GoogleLoginReturnTests(unittest.IsolatedAsyncioTestCase):
    async def test_state_mismatch_or_missing_never_calls_backend(self):
        cases = [
            ("estado-da-aba", "code=c&state=outro"),
            ("", "code=c&state=estado-da-aba"),
            ("estado-da-aba", "state=estado-da-aba"),
            ("estado-da-aba", "error=access_denied&state=estado-da-aba"),
        ]
        for expected, query in cases:
            with self.subTest(query=query, expected=expected):
                state = google_state(_google_state=expected)
                at_return(state, query)
                with patch(REQUEST, new_callable=AsyncMock) as request:
                    events = await run(State.finish_google_login, state)
                request.assert_not_awaited()
                self.assertEqual(redirects(events), ["/login"])
                self.assertEqual(state.login_message, GOOGLE_LOGIN_FAILED)
                self.assertFalse(state.is_authenticated)
                self.assertEqual(state._google_state, "")

    async def test_return_is_single_use_in_the_tab(self):
        state = google_state(_google_state="estado-da-aba")
        at_return(state, "code=c&state=estado-da-aba")
        with patch(REQUEST, new_callable=AsyncMock, side_effect=XanoRequestError(GOOGLE_LOGIN_FAILED)):
            await run(State.finish_google_login, state)
        with patch(REQUEST, new_callable=AsyncMock) as request:
            await run(State.finish_google_login, state)
        request.assert_not_awaited()

    async def test_tutor_and_veterinarian_get_session_without_vettech_password(self):
        for session, me, calls in (
            (TUTOR_SESSION, {"perfil": "tutor", "identidade_id": 7, "nome": "Ana"}, 4),
            (VET_SESSION, {"perfil": "veterinario", "identidade_id": 9, "nome": "Dr. Bia"}, 2),
        ):
            with self.subTest(perfil=session["perfil"]):
                state = google_state(_google_state="estado-da-aba")
                at_return(state, "code=c&state=estado-da-aba")
                with patch(REQUEST, new_callable=AsyncMock, side_effect=[session, me, [], []]) as request:
                    events = await run(State.finish_google_login, state)
                payload = request.await_args_list[0].kwargs["json_payload"]
                self.assertEqual(payload, {"code": "c", "state": "estado-da-aba"})
                self.assertEqual(request.await_args_list[1].args[2], f"{session['perfil']}/me")
                self.assertEqual(request.await_count, calls)
                self.assertTrue(state.is_authenticated)
                self.assertEqual(state.profile, session["perfil"])
                self.assertEqual(state._auth_token, "google-token")
                self.assertEqual(redirects(events), ["/"])
                self.assertFalse(state.is_busy)

    async def test_unexpected_backend_answer_never_opens_session(self):
        for result in ({"resultado": "confirmar_senha", "confirmacao": "x", "email": "a@b.invalid"},
                       {"authToken": "token-sem-resultado", "perfil": "tutor", "identidade_id": 7}, None):
            with self.subTest(result=result):
                state = google_state(_google_state="estado-da-aba")
                at_return(state, "code=c&state=estado-da-aba")
                with patch(REQUEST, new_callable=AsyncMock, return_value=result) as request:
                    events = await run(State.finish_google_login, state)
                request.assert_awaited_once()
                self.assertFalse(state.is_authenticated)
                self.assertEqual(state._auth_token, "")
                self.assertEqual(state.login_message, GOOGLE_LOGIN_FAILED)
                self.assertEqual(redirects(events), ["/login"])

    async def test_no_account_message_returns_to_login(self):
        state = google_state(_google_state="estado-da-aba")
        at_return(state, "code=c&state=estado-da-aba")
        with patch(REQUEST, new_callable=AsyncMock, side_effect=XanoRequestError(GOOGLE_LOGIN_NO_ACCOUNT, 403)):
            events = await run(State.finish_google_login, state)
        self.assertEqual(redirects(events), ["/login"])
        self.assertEqual(state.login_message, GOOGLE_LOGIN_NO_ACCOUNT)
        self.assertFalse(state.is_authenticated)

    async def test_logout_during_return_discards_late_response(self):
        state = google_state(_google_state="estado-da-aba")
        at_return(state, "code=c&state=estado-da-aba")

        async def late_response(*args, **kwargs):
            state._clear_session()
            return TUTOR_SESSION

        with patch(REQUEST, new_callable=AsyncMock, side_effect=late_response) as request:
            events = await run(State.finish_google_login, state)
        request.assert_awaited_once()
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertEqual(redirects(events), [])

    async def test_authenticated_user_opening_return_without_pending_login_is_kept(self):
        state = google_state(is_authenticated=True, _auth_token="sessao-atual", profile="tutor")
        at_return(state, "")
        with patch(REQUEST, new_callable=AsyncMock) as request:
            events = await run(State.finish_google_login, state)
        request.assert_not_awaited()
        self.assertEqual(redirects(events), ["/"])
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state._auth_token, "sessao-atual")


if __name__ == "__main__":
    unittest.main()
