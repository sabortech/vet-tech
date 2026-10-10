import unittest
from unittest.mock import AsyncMock, patch

from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError


def make_state():
    state = State(_reflex_internal_init=True)
    state.login_message = ""
    state.is_authenticated = False
    state.is_busy = False
    state.is_registering = False
    state.signup_message = ""
    state.signup_cpf = ""
    state.pet_message = ""
    state.is_loading_pets = False
    state.pet_name = ""
    state.selected_species_id = ""
    state.selected_breed_id = ""
    state.pet_sex = ""
    state.pet_birth_date = ""
    state.pet_weight = ""
    state.pet_coat_color = ""
    state.pet_microchip = ""
    state.species_options = []
    state.breed_options = []
    state.pets = []
    state._auth_token = ""
    return state


class AuthStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_signup_success_returns_to_login_without_authentication(self):
        state = make_state()
        state.is_registering = True
        state.signup_cpf = "529.982.247-25"
        form_data = {
            "nome": "  Ana Silva ",
            "cpf": "529.982.247-25",
            "email": " ANA@example.com ",
            "telefone": "(11) 99999-9999",
            "endereco": " Rua A, 10 ",
            "password": "secret",
        }

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
        ) as request:
            await State.signup.fn(state, form_data)

        request.assert_awaited_once_with(
            "POST",
            "H62nB-j2",
            "tutor/signup",
            json_payload={
                "nome": "Ana Silva",
                "cpf": "52998224725",
                "email": "ana@example.com",
                "telefone": "(11) 99999-9999",
                "endereco": "Rua A, 10",
                "password": "secret",
            },
        )
        self.assertFalse(state.is_registering)
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertEqual(state.signup_cpf, "")
        self.assertIn("Cadastro realizado", state.login_message)
        self.assertFalse(state.is_busy)

    async def test_signup_failure_keeps_registration_open_and_displays_error(self):
        state = make_state()
        state.is_registering = True
        state.signup_cpf = "529.982.247-25"

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=XanoRequestError("E-mail já cadastrado."),
        ) as request:
            await State.signup.fn(
                state,
                {
                    "nome": "Ana Silva",
                    "cpf": "52998224725",
                    "email": "ana@example.com",
                    "telefone": "11999999999",
                    "endereco": "Rua A, 10",
                    "password": "secret",
                },
            )

        request.assert_awaited_once()
        self.assertTrue(state.is_registering)
        self.assertEqual(state.signup_cpf, "529.982.247-25")
        self.assertEqual(state.signup_message, "E-mail já cadastrado.")
        self.assertFalse(state.is_authenticated)
        self.assertFalse(state.is_busy)

    async def test_signup_rejects_invalid_cpf_without_request(self):
        state = make_state()
        state.is_registering = True

        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock) as request:
            await State.signup.fn(
                state,
                {
                    "nome": "Ana Silva",
                    "cpf": "11111111111",
                    "email": "ana@example.com",
                    "telefone": "11999999999",
                    "endereco": "Rua A, 10",
                    "password": "secret",
                },
            )

        request.assert_not_awaited()
        self.assertTrue(state.is_registering)
        self.assertEqual(state.signup_message, "Informe um CPF válido.")

    async def test_login_success_loads_profile_data_with_shared_session(self):
        state = make_state()

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=[{"authToken": "session-token"}, [], []],
        ) as request:
            await State.login.fn(
                state,
                {"email": "ana@example.com", "password": "secret"},
            )

        self.assertTrue(state.is_authenticated)
        self.assertEqual(state._auth_token, "session-token")
        self.assertEqual(request.await_count, 3)
        self.assertEqual(state.pets, [])
        self.assertFalse(state.is_busy)


if __name__ == "__main__":
    unittest.main()
