import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state, submit_login
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError


def signed_in_state():
    state = make_state()
    state._auth_token = "test-session"
    state.is_authenticated = True
    state.species_options = [{"id": "1", "nome": "Cachorro"}]
    return state


async def open_pet(state, pet_id):
    return [update async for update in State.open_pet.fn(state, pet_id)]


def pet(pet_id="1", **extra):
    return {"id": int(pet_id), "nome": "Pet " + pet_id, "especie_id": 1, "raca_id": 0, **extra}


class PetSelectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_selection_is_pending_until_authorized_and_preserves_zero(self):
        state = signed_in_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value=pet(peso_atual=0)) as request:
            event = State.open_pet.fn(state, "1")
            await event.__anext__()
            self.assertTrue(state.is_loading_pet)
            self.assertEqual(state.selected_pet_id, "")
            request.assert_not_awaited()
            _ = [item async for item in event]
        request.assert_awaited_once_with("GET", "vettech-pets", "pets/1", auth_token="test-session")
        self.assertEqual(state.selected_pet_id, "1")
        self.assertEqual(state.selected_pet["raca"], "SRD")
        self.assertEqual(state.selected_pet["peso_atual"], "0")
        self.assertEqual(state.selected_pet["data_nasc"], "")
        self.assertFalse(state.is_loading_pet)

    async def test_bad_ids_and_missing_session_never_request_data(self):
        for value in ("0", "-1", "abc", "", "١"):
            with self.subTest(value=value):
                state = signed_in_state()
                with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock) as request:
                    await open_pet(state, value)
                request.assert_not_awaited()
                self.assertFalse(state.selected_pet_id)
        state = make_state()
        await open_pet(state, "1")
        self.assertFalse(state.is_authenticated)

    async def test_different_pet_response_is_rejected(self):
        state = signed_in_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value=pet("2")):
            await open_pet(state, "1")
        self.assertEqual(state.selected_pet, {})
        self.assertIn("incompatíveis", state.pet_detail_message)

    async def test_late_response_or_error_cannot_replace_newer_selection(self):
        for late_error in (False, True):
            with self.subTest(late_error=late_error):
                state = signed_in_state()
                started = asyncio.Event()
                release = asyncio.Event()

                async def request(method, group, endpoint, **kwargs):
                    if endpoint == "pets/1":
                        started.set()
                        await release.wait()
                        if late_error:
                            raise XanoRequestError("Old error", status_code=401)
                        return pet("1")
                    return pet("2")

                with patch("vet_tech.features.auth.state.xano_request", side_effect=request):
                    pending = asyncio.create_task(open_pet(state, "1"))
                    await started.wait()
                    await open_pet(state, "2")
                    release.set()
                    await pending
                self.assertEqual(state.selected_pet_id, "2")
                self.assertEqual(state.pet_detail_message, "")
                self.assertFalse(state.is_loading_pet)
                self.assertTrue(state.is_authenticated)

    async def test_close_or_logout_invalidates_pending_response(self):
        for logout in (False, True):
            state = signed_in_state()
            started, release = asyncio.Event(), asyncio.Event()

            async def request(*args, **kwargs):
                started.set()
                await release.wait()
                return pet()

            with patch("vet_tech.features.auth.state.xano_request", side_effect=request):
                pending = asyncio.create_task(open_pet(state, "1"))
                await started.wait()
                if logout:
                    await State.logout.fn(state)
                else:
                    State.close_pet.fn(state)
                release.set()
                await pending
            self.assertFalse(state.selected_pet_id)
            self.assertFalse(state.pet_target_id)
            self.assertFalse(state.is_loading_pet)

    async def test_catalog_failure_does_not_hide_pet_but_401_expires_session(self):
        for status in (503, 401):
            state = signed_in_state()
            with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                       side_effect=[pet(raca_id=2), XanoRequestError("Catálogo indisponível", status_code=status)]):
                await open_pet(state, "1")
            if status == 401:
                self.assertFalse(state.is_authenticated)
                self.assertEqual(state.selected_pet, {})
            else:
                self.assertEqual(state.selected_pet_id, "1")
                self.assertEqual(state.selected_pet["raca"], "Raça")
                self.assertIn("Catálogo", state.pet_detail_message)

    async def test_failed_switch_clears_previous_details_and_retry_works(self):
        state = signed_in_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[pet(), XanoRequestError("Não disponível", status_code=404), pet("2")]):
            await open_pet(state, "1")
            await open_pet(state, "2")
            self.assertEqual(state.selected_pet, {})
            self.assertEqual(state.pet_target_id, "2")
            _ = [item async for item in State.retry_pet.fn(state)]
        self.assertEqual(state.selected_pet_id, "2")

    async def test_refresh_revalidates_or_clears_selection_and_keeps_create_form(self):
        for result in ([pet()], [], XanoRequestError("Falha transitória")):
            state = signed_in_state()
            state.pet_name = "Novo pet ainda não enviado"
            with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value=pet()):
                await open_pet(state, "1")
            responses = [result, pet(nome="Atualizado")] if isinstance(result, list) and result else [result]
            with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, side_effect=responses) as request:
                _ = [update async for update in State.refresh_pets.fn(state)]
            if isinstance(result, list) and result:
                self.assertEqual(state.selected_pet["nome"], "Atualizado")
                self.assertEqual(request.await_count, 2)
            else:
                self.assertFalse(state.selected_pet_id)
            self.assertEqual(state.pet_name, "Novo pet ainda não enviado")

    async def test_new_session_clears_selection_even_if_its_list_fails(self):
        state = signed_in_state()
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock, return_value=pet()):
            await open_pet(state, "1")
        with patch("vet_tech.features.auth.state.xano_request", new_callable=AsyncMock,
                   side_effect=[{"authToken": "new-session", "perfil": "tutor", "identidade_id": 1}, {"perfil": "tutor", "identidade_id": 1}, [], XanoRequestError("Falha")]):
            await submit_login(state, {"email": "new@example.invalid", "password": "fake"})
        self.assertFalse(state.selected_pet_id)
        self.assertEqual(state.pets, [])

    async def test_old_session_list_cannot_restore_data_after_logout(self):
        state = signed_in_state()
        started, release = asyncio.Event(), asyncio.Event()

        async def request(*args, **kwargs):
            started.set()
            await release.wait()
            return [pet()]

        with patch("vet_tech.features.auth.state.xano_request", side_effect=request):
            pending = asyncio.create_task(state._load_pets())
            await started.wait()
            await State.logout.fn(state)
            release.set()
            await pending
        self.assertEqual(state.pets, [])
        self.assertEqual(state.selected_pet, {})
        self.assertFalse(state.is_loading_pets)
