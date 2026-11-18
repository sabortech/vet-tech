import unittest
from unittest.mock import AsyncMock, patch

from test_auth_state import make_state
from vet_tech.features.adoption.state import project_adoption_pet
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError


ADOPTION_PET = {
    "id": 41,
    "nome": "Luna",
    "especie_nome": "Cão",
    "raca_nome": "SRD",
    "sexo": "fêmea",
    "data_nasc": "2021-06-03",
    "peso_atual": 12000,
    "foto": "https://images.example.invalid/luna.jpg",
    "vacina": {
        "nome": "Antirrábica",
        "data_aplicacao": "2026-01-03",
        "data_prox_dose": "2027-01-03",
    },
    "medicamentos": [
        {
            "nome": "Medicamento autorizado",
            "dose": 2,
            "unidade": "mg",
            "frequencia": "1 vez ao dia",
            "tipo": "continuo",
            "data_inicio": "2026-01-03",
            "data_fim": None,
        }
    ],
    "doencas": [{"nome": "Condição autorizada", "estado": "em_tratamento"}],
    "exame": {"tipo": "Hemograma", "data": "2026-01-04", "estado": "realizado"},
}


def authenticated_state():
    state = make_state()
    state.is_authenticated = True
    state.profile = "tutor"
    state.identity_id = "12"
    state._auth_token = "synthetic-token"
    return state


class AdoptionStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_opt_in_demo_uses_local_profiles_and_never_calls_adoption_api(self):
        state = authenticated_state()
        state.pets = [{"id": "7", "nome": "Pet real"}]
        with (
            patch(
                "vet_tech.features.adoption.state.adoption_demo_enabled",
                return_value=True,
            ),
            patch(
                "vet_tech.features.adoption.state.xano_request",
                new_callable=AsyncMock,
            ) as request,
        ):
            State.load_adoption.fn(state)

            self.assertTrue(state.adoption_is_demo)
            self.assertEqual(
                [pet["nome"] for pet in state.adoption_pets],
                ["Hades", "Lua", "Lulu", "Luna", "Nina", "Pituco"],
            )
            for pet in state.adoption_pets:
                self.assertTrue(pet["foto"].startswith("/petsadocao/"))
                self.assertEqual(pet["vacina_resumo"], "Não informado")
                self.assertEqual(pet["medicamentos_resumo"], "Não informado")
                self.assertEqual(pet["doencas_resumo"], "Não informado")
                self.assertEqual(pet["exame_resumo"], "Não informado")

            State.open_adoption_preview.fn(state, state.adoption_pets[0]["id"])
            State.open_adoption_confirmation.fn(state, state.adoption_pets[0]["id"])
            State.confirm_adoption.fn(state)

            request.assert_not_awaited()
            self.assertEqual([pet["nome"] for pet in state.adoption_pets], ["Lua", "Lulu", "Luna", "Nina", "Pituco"])
            self.assertEqual(state.pets, [{"id": "7", "nome": "Pet real"}])
            self.assertIn("Simulação", state.adoption_message)
            self.assertIn("Nada foi salvo no Xano", state.adoption_message)
            self.assertFalse(state.adoption_confirmation_open)

            State.load_adoption.fn(state)

        request.assert_not_awaited()
        self.assertEqual([pet["nome"] for pet in state.adoption_pets], ["Lua", "Lulu", "Luna", "Nina", "Pituco"])

    async def test_demo_mode_is_disabled_by_default(self):
        with patch.dict("os.environ", {}, clear=False):
            from vet_tech.shared.config import adoption_demo_enabled

            with patch.dict("os.environ", {"VET_TECH_ADOPTION_DEMO": "false"}):
                self.assertFalse(adoption_demo_enabled())
            with patch.dict("os.environ", {"VET_TECH_ADOPTION_DEMO": "true"}):
                self.assertTrue(adoption_demo_enabled())

    def test_projection_only_keeps_authorized_clinical_summary(self):
        source = {
            **ADOPTION_PET,
            "tutor_id": 88,
            "num_microchip": 123,
            "veterinario_nome": "Profissional identificável",
            "diagnostico": "Texto clínico privado",
            "resultado": "Resultado privado",
            "anexos": ["privado"],
        }
        projected = project_adoption_pet(source)
        self.assertEqual(projected["id"], "41")
        self.assertEqual(projected["sexo"], "Fêmea")
        self.assertIn("Antirrábica", projected["vacina_resumo"])
        self.assertIn("Medicamento autorizado", projected["medicamentos_resumo"])
        self.assertIn("Condição autorizada", projected["doencas_resumo"])
        self.assertIn("Hemograma", projected["exame_resumo"])
        serialized = repr(projected)
        for forbidden in ("tutor_id", "microchip", "Profissional identificável", "Texto clínico privado", "Resultado privado", "privado"):
            self.assertNotIn(forbidden, serialized)

    async def test_authenticated_entry_loads_once_and_empty_response_is_valid(self):
        state = authenticated_state()
        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
            return_value=[],
        ) as request:
            event = State.load_adoption.fn(state)
            self.assertTrue(state.is_loading_adoption)
            await State.fetch_adoption.fn(
                state, state._adoption_generation, state._session_generation
            )
        self.assertIsNotNone(event)
        request.assert_awaited_once_with(
            "GET", "vettech-pets", "adoption", auth_token="synthetic-token"
        )
        self.assertEqual(state.adoption_pets, [])
        self.assertFalse(state.is_loading_adoption)

    async def test_list_failure_preserves_cached_items_and_exposes_recovery_message(self):
        state = authenticated_state()
        state.adoption_pets = [project_adoption_pet(ADOPTION_PET)]
        State.load_adoption.fn(state)
        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
            side_effect=XanoRequestError("Falha de conexão."),
        ):
            await State.fetch_adoption.fn(
                state, state._adoption_generation, state._session_generation
            )
        self.assertEqual([pet["id"] for pet in state.adoption_pets], ["41"])
        self.assertTrue(state.adoption_error)
        self.assertEqual(state.adoption_message, "Falha de conexão.")
        self.assertFalse(state.is_loading_adoption)

    async def test_explicit_refresh_starts_one_new_list_request(self):
        state = authenticated_state()
        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
            side_effect=[[ADOPTION_PET], [ADOPTION_PET]],
        ) as request:
            State.load_adoption.fn(state)
            await State.fetch_adoption.fn(
                state, state._adoption_generation, state._session_generation
            )
            State.load_adoption.fn(state)
            await State.fetch_adoption.fn(
                state, state._adoption_generation, state._session_generation
            )
        self.assertEqual(request.await_count, 2)
        self.assertEqual([pet["id"] for pet in state.adoption_pets], ["41"])
        self.assertFalse(state.is_loading_adoption)

    def test_load_entry_redirects_unauthenticated_or_non_tutor_without_api(self):
        state = make_state()
        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
        ) as request:
            redirect = State.load_adoption.fn(state)
            self.assertIsNotNone(redirect)
            state.is_authenticated = True
            state.profile = "veterinario"
            state._auth_token = "synthetic-token"
            redirect = State.load_adoption.fn(state)
        request.assert_not_awaited()
        self.assertIn("redirect", str(redirect))

    async def test_preview_and_cancel_do_not_make_requests(self):
        state = authenticated_state()
        state.adoption_pets = [project_adoption_pet(ADOPTION_PET)]
        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
        ) as request:
            State.open_adoption_preview.fn(state, "41")
            State.open_adoption_confirmation.fn(state, "41")
            State.set_adoption_confirmation.fn(state, False)
            self.assertEqual(state.adoption_preview["id"], "41")
            self.assertFalse(state.adoption_confirmation_open)
            self.assertEqual(state.adoption_target_id, "")
            request.assert_not_awaited()

    async def test_adoption_posts_only_pet_id_and_updates_both_local_lists(self):
        state = authenticated_state()
        adoption_pet = project_adoption_pet(ADOPTION_PET)
        state.adoption_pets = [adoption_pet]
        state.pets = []
        state.selected_pet = {"id": "9", "nome": "Outro pet"}
        State.open_adoption_confirmation.fn(state, "41")
        event = State.confirm_adoption.fn(state)
        self.assertIsNotNone(event)
        self.assertIsNone(State.confirm_adoption.fn(state))
        self.assertEqual(state.adoption_busy_id, "41")

        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
            return_value={
                "id": 41,
                "nome": "Luna",
                "especie_id": 1,
                "raca_id": None,
                "sexo": "fêmea",
                "data_nasc": "2021-06-03",
                "peso_atual": 12000,
                "foto": "https://images.example.invalid/luna.jpg",
                "especie_nome": "Cão",
                "raca_nome": "SRD",
            },
        ) as request:
            await State.perform_adoption.fn(
                state, "41", state._session_generation
            )

        request.assert_awaited_once_with(
            "POST",
            "vettech-pets",
            "adoption",
            auth_token="synthetic-token",
            json_payload={"pet_id": 41},
        )
        self.assertEqual(state.adoption_pets, [])
        self.assertEqual([pet["id"] for pet in state.pets], ["41"])
        self.assertEqual(state.selected_pet["id"], "9")
        self.assertFalse(state.adoption_confirmation_open)
        self.assertEqual(state.adoption_message, "Luna agora faz parte da sua família.")
        self.assertFalse(state.adoption_error)

    async def test_failure_and_incompatible_response_preserve_confirmed_lists(self):
        for response in (
            XanoRequestError("Pet não disponível.", status_code=409),
            {"id": 99, "nome": "Outro pet"},
        ):
            with self.subTest(response=response):
                state = authenticated_state()
                state.adoption_pets = [project_adoption_pet(ADOPTION_PET)]
                previous_pets = [{"id": "7", "nome": "Existente"}]
                state.pets = previous_pets.copy()
                State.open_adoption_confirmation.fn(state, "41")
                State.confirm_adoption.fn(state)
                with patch(
                    "vet_tech.features.adoption.state.xano_request",
                    new_callable=AsyncMock,
                    side_effect=response if isinstance(response, Exception) else None,
                    return_value=response if isinstance(response, dict) else None,
                ) as request:
                    await State.perform_adoption.fn(
                        state, "41", state._session_generation
                    )
                request.assert_awaited_once()
                self.assertEqual([pet["id"] for pet in state.adoption_pets], ["41"])
                self.assertEqual(state.pets, previous_pets)
                self.assertTrue(state.adoption_confirmation_open)
                self.assertTrue(state.adoption_error)
                self.assertEqual(state.adoption_busy_id, "")

    async def test_stale_list_response_after_session_clear_is_ignored(self):
        state = authenticated_state()

        async def clear_then_return(*args, **kwargs):
            state._clear_session()
            return [ADOPTION_PET]

        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
            side_effect=clear_then_return,
        ):
            State.load_adoption.fn(state)
            await State.fetch_adoption.fn(
                state, state._adoption_generation, state._session_generation
            )
        self.assertEqual(state.adoption_pets, [])
        self.assertFalse(state.is_authenticated)
        self.assertFalse(state.is_loading_adoption)

    async def test_stale_adoption_response_after_session_clear_does_not_mutate_new_session(self):
        state = authenticated_state()
        state.adoption_pets = [project_adoption_pet(ADOPTION_PET)]
        State.open_adoption_confirmation.fn(state, "41")
        State.confirm_adoption.fn(state)

        async def clear_then_return(*args, **kwargs):
            state._clear_session()
            return {
                "id": 41,
                "nome": "Luna",
                "especie_id": 1,
                "especie_nome": "Cão",
                "raca_nome": "SRD",
            }

        with patch(
            "vet_tech.features.adoption.state.xano_request",
            new_callable=AsyncMock,
            side_effect=clear_then_return,
        ):
            await State.perform_adoption.fn(
                state, "41", state._session_generation
            )
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.adoption_pets, [])
        self.assertEqual(state.pets, [])
        self.assertFalse(state.adoption_confirmation_open)
        self.assertFalse(state.adoption_busy_id)


if __name__ == "__main__":
    unittest.main()
