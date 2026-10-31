import unittest
import reflex as rx
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from vet_tech.features.auth.state import (
    State,
    display_pet_sex,
    format_pet_birth_date,
)
from vet_tech.shared.xano_client import XanoRequestError


def make_state():
    from vet_tech.features.settings.state import SettingsState
    root = rx.State(_reflex_internal_init=True)
    state = root.get_substate(State.get_full_name().split("."))
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


async def submit_signup(state, data):
    return [event async for event in State.signup.fn(state, data)]


async def submit_login(state, data):
    return [event async for event in State.login.fn(state, data)]


async def submit_pet(state, files):
    return [item for event in [event async for event in State.create_pet.fn(state, files) if event is not None] for item in (event if isinstance(event, list) else [event])]


class AuthStateTests(unittest.IsolatedAsyncioTestCase):
    def test_pet_display_formatting_preserves_unknown_values(self):
        self.assertEqual(format_pet_birth_date("2026-10-05"), "05/10/2026")
        self.assertEqual(
            format_pet_birth_date("2026-10-05T11:30:00Z"),
            "05/10/2026",
        )
        self.assertEqual(format_pet_birth_date("data inválida"), "data inválida")
        self.assertEqual(display_pet_sex("macho"), "Macho")
        self.assertEqual(display_pet_sex("Masc"), "Macho")
        self.assertEqual(display_pet_sex("FEM"), "Fêmea")
        self.assertEqual(display_pet_sex("Outro"), "Outro")

    async def test_password_confirmation_and_required_fields_block_api(self):
        data = {
            "nome": "Ana Silva", "cpf": "52998224725",
            "email": "ana@example.invalid", "telefone": "11999999999",
            "endereco": "Rua A", "password": "secret",
            "password_confirmation": "secret",
        }
        cases = [dict(data, password_confirmation="different"),
                 {key: value for key, value in data.items() if key != "password_confirmation"},
                 dict(data, endereco="")]
        for case in cases:
            with self.subTest(case=list(case)):
                state = make_state()
                with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock) as request:
                    await submit_signup(state, case)
                request.assert_not_awaited()
                self.assertTrue(state.signup_message)
                self.assertFalse(state.is_busy)

    async def test_busy_state_is_sent_before_api_and_blocks_repeat(self):
        state = make_state()
        data = {
            "nome": "Ana Silva", "cpf": "52998224725",
            "email": "ana@example.invalid", "telefone": "11999999999",
            "endereco": "Rua A", "password": "secret",
            "password_confirmation": "secret",
        }
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock) as request:
            pending = State.signup.fn(state, data)
            await pending.__anext__()
            self.assertTrue(state.is_busy)
            request.assert_not_awaited()
            await submit_signup(state, data)
            request.assert_not_awaited()
            events = [event async for event in pending]
        request.assert_awaited_once()
        self.assertFalse(state.is_busy)
        self.assertTrue(events)

    def test_login_registration_entry_redirects_to_single_route(self):
        state = make_state()
        event = State.show_signup.fn(state)
        self.assertEqual(event.args[0][1]._var_value, "/cadastro")

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
            "password_confirmation": "secret",
        }

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
        ) as request:
            events = await submit_signup(state, form_data)

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
        self.assertEqual(events[-1].args[0][1]._var_value, "/login")

    async def test_signup_failure_keeps_registration_open_and_displays_error(self):
        state = make_state()
        state.is_registering = True
        state.signup_cpf = "529.982.247-25"

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=XanoRequestError("E-mail já cadastrado."),
        ) as request:
            await submit_signup(
                state,
                {
                    "nome": "Ana Silva",
                    "cpf": "52998224725",
                    "email": "ana@example.com",
                    "telefone": "11999999999",
                    "endereco": "Rua A, 10",
                    "password": "secret",
                    "password_confirmation": "secret",
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
            await submit_signup(
                state,
                {
                    "nome": "Ana Silva",
                    "cpf": "11111111111",
                    "email": "ana@example.com",
                    "telefone": "11999999999",
                    "endereco": "Rua A, 10",
                    "password": "secret",
                    "password_confirmation": "secret",
                },
            )

        request.assert_not_awaited()
        self.assertTrue(state.is_registering)
        self.assertEqual(state.signup_message, "Informe um CPF válido.")

    async def test_login_publishes_busy_and_session_before_auxiliary_requests(self):
        state = make_state()
        state.pets = [{"id": "old", "nome": "Anterior"}]
        data = {"email": "ana@example.invalid", "password": "secret"}
        with patch("vet_tech.features.auth.state.xano_request",
                   new_callable=AsyncMock,
                   side_effect=[{"authToken": "session-token", "perfil": "tutor", "identidade_id": 1}, {"perfil": "tutor", "identidade_id": 1}, [], []]) as request:
            events = State.login.fn(state, data)
            await anext(events)
            self.assertTrue(state.is_busy)
            self.assertFalse(state.is_authenticated)
            request.assert_not_awaited()
            await submit_login(state, data)
            request.assert_not_awaited()

            await anext(events)
            self.assertEqual(request.await_count, 2)
            self.assertTrue(state.is_authenticated)
            self.assertTrue(state.is_loading_pets)
            self.assertEqual(state.pets, [])
            self.assertEqual(state._auth_token, "session-token")
            await submit_login(state, data)
            self.assertEqual(request.await_count, 2)
            async for _ in events:
                pass
        self.assertFalse(state.is_busy)
        self.assertFalse(state.is_loading_pets)
        self.assertEqual(request.await_count, 4)

    async def test_login_validation_and_rejection_release_form(self):
        state = make_state()
        with patch("vet_tech.features.auth.state.xano_request",
                   new_callable=AsyncMock,
                   side_effect=XanoRequestError("Credenciais inválidas.")) as request:
            await submit_login(state, {"email": "", "password": ""})
            request.assert_not_awaited()
            await submit_login(state, {"email": "ana@example.invalid", "password": "wrong"})
        request.assert_awaited_once()
        self.assertEqual(state.login_message, "Credenciais inválidas.")
        self.assertFalse(state.is_authenticated)
        self.assertFalse(state.is_busy)
        self.assertFalse(state.is_loading_pets)
        self.assertEqual(state._auth_token, "")

    async def test_login_success_loads_profile_data_with_shared_session(self):
        state = make_state()

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=[{"authToken": "session-token", "perfil": "tutor", "identidade_id": 1},
                         {"perfil": "tutor", "identidade_id": 1, "nome": "Tutor"}, [], []],
        ) as request:
            await submit_login(
                state,
                {"email": "ana@example.com", "password": "secret"},
            )

        self.assertTrue(state.is_authenticated)
        self.assertEqual(state._auth_token, "session-token")
        self.assertEqual(request.await_count, 4)
        self.assertEqual(state.pets, [])
        self.assertFalse(state.is_busy)

    async def test_login_rate_limit_preserves_actionable_message_and_releases_form(self):
        state = make_state()
        message = (
            "O Xano limitou temporariamente as solicitações. "
            "Aguarde alguns instantes e tente novamente."
        )
        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=XanoRequestError(message),
        ) as request:
            await submit_login(
                state, {"email": "fixture@example.invalid", "password": "synthetic"}
            )
        request.assert_awaited_once()
        self.assertEqual(state.login_message, message)
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertFalse(state.is_busy)

    async def test_srd_pet_with_empty_optional_fields_needs_no_breed_request(self):
        state = make_state()
        state._auth_token = "session-token"
        state.species_options = [{"id": "1", "nome": "Cachorro"}]
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   return_value=[{"id": 10, "nome": "Rex", "especie_id": 1,
                                  "raca_id": None, "sexo": None, "data_nasc": None,
                                  "peso_atual": 0}] ) as request:
            await state._load_pets()
        request.assert_awaited_once_with("GET", "vettech-pets", "pets", auth_token="session-token")
        self.assertEqual(state.pets[0]["raca"], "SRD")
        self.assertEqual(state.pets[0]["sexo"], "")
        self.assertEqual(state.pets[0]["data_nasc"], "")
        self.assertEqual(state.pets[0]["foto"], "")
        self.assertEqual(state.pets[0]["metadados"], "Cachorro · SRD")
        self.assertEqual(state.pets[0]["peso_atual"], "0")
        self.assertFalse(state.is_loading_pets)

    async def test_pet_list_maps_authenticated_photo_url_and_optional_metadata(self):
        state = make_state()
        state._auth_token = "session-token"
        state.species_options = [{"id": "1", "nome": "Cachorro"}]

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            return_value=[
                {
                    "id": 10,
                    "nome": "Rex",
                    "especie_id": 1,
                    "sexo": "Masc",
                    "data_nasc": "2026-10-05",
                    "foto": {"url": "https://cdn.example.invalid/rex.jpg"},
                }
            ],
        ):
            await state._load_pets()

        self.assertEqual(state.pets[0]["foto"], "https://cdn.example.invalid/rex.jpg")
        self.assertEqual(state.pets[0]["sexo"], "Macho")
        self.assertEqual(state.pets[0]["data_nasc"], "05/10/2026")
        self.assertEqual(state.pets[0]["metadados"], "Cachorro · SRD · Macho · 05/10/2026")

    async def test_pet_list_does_not_expose_private_storage_path_as_photo_url(self):
        state = make_state()
        state._auth_token = "session-token"

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            return_value=[
                {
                    "id": 11,
                    "nome": "Luna",
                    "foto": {
                        "access": "private",
                        "path": "private/luna.jpg",
                    },
                }
            ],
        ):
            await state._load_pets()

        self.assertEqual(state.pets[0]["foto"], "")

    async def test_breed_failure_still_displays_all_pets(self):
        state = make_state()
        state._auth_token = "session-token"
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[[{"id": 10, "nome": "Rex", "especie_id": 1, "raca_id": 2},
                                 {"id": 11, "nome": "Luna", "especie_id": 2, "raca_id": 3}],
                                XanoRequestError("Catálogo indisponível"),
                                [{"id": 3, "nome": "Siamês"}]]):
            await state._load_pets()
        self.assertEqual([pet["nome"] for pet in state.pets], ["Rex", "Luna"])
        self.assertEqual(state.pets[0]["raca"], "")
        self.assertEqual(state.pets[0]["metadados"], "")
        self.assertEqual(state.pets[1]["raca"], "Siamês")
        self.assertEqual(state.pets[1]["metadados"], "Siamês")
        self.assertIn("Catálogo indisponível", state.pet_message)

    async def test_species_failure_keeps_new_session_and_loads_its_pets(self):
        state = make_state()
        state.pets = [{"id": "old", "nome": "Pet de outro tutor"}]
        state.species_options = [{"id": "99", "nome": "Antiga"}]
        state.breed_options = [{"id": "99", "nome": "Antiga"}]
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[{"authToken": "new-session", "perfil": "tutor", "identidade_id": 1},
                                {"perfil": "tutor", "identidade_id": 1}, XanoRequestError("Catálogo indisponível"),
                                [{"id": 10, "nome": "Rex", "especie_id": 1}]] ) as request:
            await submit_login(state, {"email": "novo@example.invalid", "password": "secret"})
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state._auth_token, "new-session")
        self.assertEqual([pet["id"] for pet in state.pets], ["10"])
        self.assertEqual(state.species_options, [])
        self.assertEqual(state.breed_options, [])
        self.assertEqual(request.await_args_list[-1].kwargs["auth_token"], "new-session")

    async def test_new_session_does_not_keep_previous_pets_when_list_fails(self):
        state = make_state()
        state.pets = [{"id": "old", "nome": "Pet de outro tutor"}]
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[{"authToken": "new-session", "perfil": "tutor", "identidade_id": 1},
                                {"perfil": "tutor", "identidade_id": 1}, [], XanoRequestError("Falha na lista")]):
            await submit_login(state, {"email": "novo@example.invalid", "password": "secret"})
        self.assertEqual(state.pets, [])
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.pet_message, "Falha na lista")

    async def test_list_failure_preserves_current_session_pets_and_empty_success_clears_them(self):
        state = make_state()
        state._auth_token = "session-token"
        state.pets = [{"id": "10", "nome": "Rex"}]
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=XanoRequestError("Falha na lista")):
            await state._load_pets()
        self.assertEqual(state.pets[0]["nome"], "Rex")
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value=[]):
            _ = [update async for update in State.refresh_pets.fn(state)]
        self.assertEqual(state.pets, [])
        self.assertEqual(state.pet_message, "")

    async def test_create_srd_pet_refreshes_list_without_client_owner_or_breed(self):
        state = make_state()
        state._auth_token = "session-token"
        state.pet_name = "Rex"
        state.selected_species_id = "1"
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[{"id": 10}, [{"id": 10, "nome": "Rex", "especie_id": 1,
                                            "raca_id": None}]]) as request:
            await submit_pet(state, [])
        self.assertEqual(request.await_count, 2)
        self.assertEqual(request.await_args_list[0].kwargs["json_payload"], {"nome": "Rex", "especie_id": "1"})
        self.assertEqual(state.pets[0]["raca"], "SRD")
        self.assertEqual(state.pet_message, "Pet cadastrado com sucesso.")

    async def test_create_pet_preserves_iso_birth_date_in_xano_payload(self):
        state = make_state()
        state._auth_token = "session-token"
        state.pet_name = "Rex"
        state.selected_species_id = "1"
        state.pet_birth_date = "2026-10-05"
        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=[{"id": 10}, []],
        ) as request:
            events = await submit_pet(state, [])
        self.assertEqual(
            request.await_args_list[0].kwargs["json_payload"],
            {
                "nome": "Rex",
                "especie_id": "1",
                "data_nasc": "2026-10-05",
            },
        )
        self.assertEqual(len(events), 2)

    async def test_create_pet_with_photo_sends_base64_data_uri_and_clears_selection(self):
        state = make_state()
        state._auth_token = "session-token"
        state.pet_name = "Rex"
        state.selected_species_id = "1"
        upload = SimpleNamespace(
            name="rex.png",
            content_type="image/png",
            read=AsyncMock(return_value=b"image-bytes"),
        )

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            side_effect=[{"id": 10}, []],
        ) as request:
            events = await submit_pet(state, [upload])

        upload.read.assert_awaited_once()
        self.assertEqual(
            request.await_args_list[0].kwargs["json_payload"],
            {
                "nome": "Rex",
                "especie_id": "1",
                "foto": "data:image/png;base64,aW1hZ2UtYnl0ZXM=",
            },
        )
        self.assertNotIn("files", request.await_args_list[0].kwargs)
        self.assertEqual(len(events), 2)

    async def test_pet_list_displays_base64_photo(self):
        state = make_state()
        state._auth_token = "session-token"
        photo = "data:image/png;base64,aW1hZ2UtYnl0ZXM="

        with patch(
            "vet_tech.features.auth.state.xano_request",
            new_callable=AsyncMock,
            return_value=[{"id": 12, "nome": "Mel", "foto": photo}],
        ):
            await state._load_pets()

        self.assertEqual(state.pets[0]["foto"], photo)


if __name__ == "__main__":
    unittest.main()
