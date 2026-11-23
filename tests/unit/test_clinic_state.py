import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError


def clinic_state():
    state = make_state()
    state.is_authenticated = True
    state.profile = "clinica"
    state.identity_id = "11"
    state._auth_token = "token-sintetico"
    return state


class ClinicStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_clinic_creates_vet_without_client_clinic_id(self):
        state = clinic_state()
        state.clinic_vet_form = "novo"
        state.professional_species = ["2"]
        state.professional_specialties = ["3"]
        form = {"nome": "Ana", "email": "ana@example.org", "telefone": "123", "crmv": "123", "crmv_uf": "SP", "password": "temporary", "password_confirmation": "temporary", "clinica_id": "999"}
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock, side_effect=[{"success": True}, []]) as request:
            async for _ in State.clinic_submit_vet.fn(state, form):
                pass
        payload = request.await_args_list[0].kwargs["json_payload"]
        self.assertNotIn("clinica_id", payload)
        self.assertEqual(payload["especies_ids"], [2])
        self.assertEqual(state.clinic_vet_form, "")

    async def test_invite_is_sent_separately_and_no_password(self):
        state = clinic_state()
        state.clinic_vet_form = "vinculo"
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock, return_value={"success": True}) as request:
            async for _ in State.clinic_submit_vet.fn(state, {"email": "Vet@Example.org"}):
                pass
        self.assertEqual(request.await_args.args[2], "clinica/veterinarios/convites")
        self.assertEqual(request.await_args.kwargs["json_payload"], {"email": "vet@example.org"})

    async def test_only_vet_can_accept_invite(self):
        state = clinic_state()
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock) as request:
            async for _ in State.accept_vet_invite.fn(state, "1"):
                pass
        request.assert_not_awaited()

    async def test_same_login_confirms_clinic_identity(self):
        state = make_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value={"perfil": "clinica", "identidade_id": 11, "nome": "Admin", "clinica_nome": "Clínica A"}) as request:
            async for _ in state._open_session({"authToken": "token", "perfil": "clinica", "identidade_id": 11}, state._session_generation):
                pass
        self.assertEqual(state.profile, "clinica")
        self.assertEqual(state.clinic_name, "Clínica A")
        self.assertTrue(state.is_authenticated)
        self.assertEqual(request.await_args.args[2], "clinica/me")

    async def test_clinic_pet_payload_never_accepts_client_owner(self):
        state = clinic_state()
        state.selected_species_id = "2"
        state.pet_name = "Lua"
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock, return_value={"id": 4, "nome": "Lua"}) as request:
            async for _ in State.clinic_create_pet.fn(state, []):
                pass
        payload = request.await_args.kwargs["json_payload"]
        self.assertEqual(payload, {"nome": "Lua", "especie_id": 2})
        self.assertEqual(state.clinic_admin_pets[0]["disponivel"], "nao")

    async def test_pet_photo_is_encoded_in_base64(self):
        state = clinic_state()
        state.selected_species_id = "2"
        state.pet_name = "Lua"
        upload = type("Photo", (), {"content_type": "image/png", "read": AsyncMock(return_value=b"abc")})()
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock, return_value={"id": 4, "nome": "Lua"}) as request:
            async for _ in State.clinic_create_pet.fn(state, [upload]):
                pass
        self.assertEqual(request.await_args.kwargs["json_payload"]["foto"], "data:image/png;base64,YWJj")

    async def test_invalid_image_is_not_sent(self):
        state = clinic_state()
        state.selected_species_id = "2"
        state.pet_name = "Lua"
        upload = type("Photo", (), {"content_type": "text/plain", "read": AsyncMock(return_value=b"abc")})()
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock) as request:
            async for _ in State.clinic_create_pet.fn(state, [upload]):
                pass
        request.assert_not_awaited()

    async def test_oversized_image_is_not_sent(self):
        state = clinic_state()
        state.selected_species_id = "2"
        state.pet_name = "Lua"
        upload = type("Photo", (), {"content_type": "image/png", "read": AsyncMock(return_value=b"x" * (1024 * 1024 + 1))})()
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock) as request:
            async for _ in State.clinic_create_pet.fn(state, [upload]):
                pass
        request.assert_not_awaited()

    def test_clinic_uses_shared_birth_date_picker(self):
        state = clinic_state()
        state.birth_calendar_open = True
        State.birth_calendar_choose_day.fn(state, "2020-01-02")
        self.assertEqual(state.pet_birth_date, "2020-01-02")

    async def test_failed_availability_does_not_change_local_list(self):
        state = clinic_state()
        state.clinic_admin_pets = [{"id": "4", "nome": "Lua", "disponivel": "nao"}]
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock, side_effect=XanoRequestError("Pet não disponível.")):
            async for _ in State.clinic_set_availability.fn(state, "4", True):
                pass
        self.assertEqual(state.clinic_admin_pets[0]["disponivel"], "nao")

    async def test_other_profiles_cannot_use_clinic_actions(self):
        state = clinic_state()
        state.profile = "tutor"
        with patch("vet_tech.features.clinic.state.xano_request", new_callable=AsyncMock) as request:
            async for _ in State.clinic_load.fn(state):
                pass
        request.assert_not_awaited()
