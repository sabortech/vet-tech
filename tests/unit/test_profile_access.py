import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state, submit_signup, submit_pet, submit_login
from vet_tech.features.auth.state import State
from vet_tech.features.veterinarians.validation import professional_payload


class ProfessionalValidationTests(unittest.TestCase):
    def test_local_format_deduplicates_links_and_clinic_is_optional(self):
        payload = professional_payload({"crmv": " ab123 ", "crmv_uf": "sp"}, ["1", "1"], ["2"], "")
        self.assertEqual(payload, {"crmv": "AB123", "crmv_uf": "SP", "especies_ids": [1], "especialidades_ids": [2], "clinica_id": None})

    def test_rejects_punctuation_unicode_internal_space_bad_uf_and_invalid_links(self):
        for crmv, uf, species in [("AB-1", "SP", ["1"]), ("１２３", "SP", ["1"]), ("A B", "SP", ["1"]),
                                   ("123", "XX", ["1"]), ("123", "SP", []), ("123", "SP", ["-1"])]:
            with self.subTest(crmv=crmv, uf=uf, species=species), self.assertRaises(ValueError):
                professional_payload({"crmv": crmv, "crmv_uf": uf}, species, ["1"], "")


class ProfileAccessTests(unittest.IsolatedAsyncioTestCase):
    async def test_veterinarian_login_verifies_identity_without_loading_tutor_pets(self):
        state = make_state()
        state.pets = [{"id": "old"}]
        state.selected_pet = {"id": "old"}
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[{"authToken": "vet-token", "perfil": "veterinario", "identidade_id": 1},
                                {"perfil": "veterinario", "identidade_id": 1, "nome": "Vet"}]) as request:
            await submit_login(state, {"email": "vet@example.org", "password": "secret"})
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.profile, "veterinario")
        self.assertEqual(state.pets, [])
        self.assertEqual(state.selected_pet_id, "")
        self.assertEqual(request.await_count, 2)
        self.assertEqual(request.await_args_list[-1].args[2], "veterinario/me")

    async def test_inconsistent_identity_never_establishes_session(self):
        state = make_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[{"authToken": "token", "perfil": "veterinario", "identidade_id": 1},
                                {"perfil": "tutor", "identidade_id": 1}]):
            await submit_login(state, {"email": "vet@example.org", "password": "secret"})
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")

    async def test_logout_during_identity_confirmation_discards_response(self):
        state = make_state()
        entered, release = asyncio.Event(), asyncio.Event()
        async def request(method, group, endpoint, **kwargs):
            if endpoint == "acesso/login":
                return {"authToken": "token", "perfil": "veterinario", "identidade_id": 1}
            entered.set()
            await release.wait()
            return {"perfil": "veterinario", "identidade_id": 1}
        with patch("vet_tech.features.auth.state.xano_request", side_effect=request):
            pending = asyncio.create_task(submit_login(state, {"email": "vet@example.org", "password": "secret"}))
            await entered.wait()
            await State.logout.fn(state)
            release.set()
            await pending
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.profile, "")

    async def test_vet_signup_uses_professional_endpoint_without_auto_login(self):
        state = make_state()
        state.signup_profile = "veterinario"
        state.professional_species = ["1"]
        state.professional_specialties = ["2"]
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock) as request:
            await submit_signup(state, {"nome": "Vet", "email": "vet@example.org", "telefone": "123", "password": "secret",
                                       "password_confirmation": "secret", "crmv": "ab123", "crmv_uf": "SP"})
        self.assertEqual(request.await_args.args[2], "veterinario/signup")
        self.assertNotIn("cpf", request.await_args.kwargs["json_payload"])
        self.assertFalse(state.is_authenticated)

    async def test_registration_catalog_selection_and_failure_are_recoverable(self):
        state = make_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   return_value={"especies": [{"id": 1, "nome": "Cachorro"}], "especialidades": [{"id": 1, "nome": "Clínica geral"}], "clinicas": []}):
            await State.choose_signup_profile.fn(state, "veterinario")
        self.assertEqual(state.registration_species[0]["id"], "1")
        self.assertEqual(state.registration_options_message, "")

    def test_menu_and_modal_do_not_implicitly_change_pet(self):
        state = make_state()
        state.profile = "tutor"
        state.selected_pet = {"id": "7"}
        State.toggle_sidebar.fn(state)
        State.change_section.fn(state, "Vacinas")
        State.set_pet_modal.fn(state, True)
        state.pet_name = "Unsaved"
        State.set_pet_modal.fn(state, False)
        self.assertEqual(state.selected_pet_id, "7")
        self.assertEqual(state.pet_name, "")
        self.assertFalse(state.pet_modal_open)
        State.show_pet_picker.fn(state)
        self.assertTrue(state.pet_picker_open)
        # Returning to the picker invalidates the pending pet load and its cache.
        self.assertEqual(state.selected_pet_id, "")

    async def test_pet_create_response_after_logout_does_not_repopulate_data(self):
        state = make_state()
        state.profile = "tutor"
        state._auth_token = "old-token"
        state.pet_name, state.selected_species_id = "Rex", "1"
        entered, release = asyncio.Event(), asyncio.Event()
        async def request(*args, **kwargs):
            entered.set()
            await release.wait()
            return {"id": 10}
        with patch("vet_tech.features.auth.state.xano_request", side_effect=request) as call:
            pending = asyncio.create_task(submit_pet(state, []))
            await entered.wait()
            await State.logout.fn(state)
            release.set()
            await pending
        self.assertEqual(call.call_count, 1)
        self.assertEqual(state.pet_message, "")
        self.assertEqual(state.pets, [])

    async def test_old_create_refresh_cannot_clear_files_in_the_next_session(self):
        state = make_state()
        state.profile = "tutor"
        state._auth_token = "old-token"
        state.pet_name, state.selected_species_id = "Rex", "1"
        entered, release = asyncio.Event(), asyncio.Event()
        async def request(method, *args, **kwargs):
            if method == "POST":
                return {"id": 10}
            entered.set()
            await release.wait()
            return []
        with patch("vet_tech.features.auth.state.xano_request", side_effect=request):
            pending = asyncio.create_task(submit_pet(state, []))
            await entered.wait()
            await State.logout.fn(state)
            state._auth_token = "new-token"
            state.pet_name = "New session draft"
            state.pet_modal_open = True
            release.set()
            result = await pending
        self.assertEqual(result, [], "An old response must not emit a browser file-clear event")
        self.assertEqual(state.pet_name, "New session draft")
        self.assertTrue(state.pet_modal_open)

    async def test_pet_busy_state_is_published_before_api_and_blocks_a_repeat(self):
        state = make_state()
        state.profile = "tutor"
        state._auth_token = "token"
        state.pet_name, state.selected_species_id = "Rex", "1"
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, side_effect=[{"id": 1}, []]) as request:
            pending = State.create_pet.fn(state, [])
            await pending.__anext__()
            self.assertTrue(state.is_busy)
            request.assert_not_awaited()
            await submit_pet(state, [])
            request.assert_not_awaited()
            _ = [update async for update in pending]
        self.assertEqual(request.await_count, 2)
        self.assertFalse(state.is_busy)
