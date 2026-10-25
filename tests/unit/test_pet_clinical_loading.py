"""Exercise scheduling, latency, session isolation and recovery with controlled IO."""
import asyncio
from contextlib import contextmanager
import time
import unittest
from unittest.mock import AsyncMock, patch

from test_clinical_state import consume, session, TARGET
from test_pet_selection import pet
from vet_tech.features.auth.state import State
from vet_tech.shared.xano_client import XanoRequestError


@contextmanager
def state_lock(state):
    """Track the lock: every HTTP callback must run outside it."""
    held = [False]

    async def enter(*args):
        held[0] = True
        return state

    async def leave(*args):
        held[0] = False

    with patch.object(State, '__aenter__', enter), patch.object(State, '__aexit__', leave):
        yield held


def selected():
    state = session()
    state.pet_target_id = '1'
    state.selected_pet = {'id': '1', 'nome': 'Pet 1'}
    return state


async def fetch(state):
    await State.fetch_tutor_clinical.fn(state, state._clinic_generation, False)


class PetClinicalLoadingTests(unittest.IsolatedAsyncioTestCase):
    async def test_selection_schedules_without_http_and_detail_schedules_clinical(self):
        state = session()
        state.species_options = [{'id': '1', 'nome': 'Cachorro'}]
        with patch('vet_tech.features.auth.state.xano_request', AsyncMock(return_value=pet())) as detail:
            events = await consume(State.open_pet.fn(state, '1'))
            detail.assert_not_awaited()
            self.assertTrue(state.is_loading_pet)
            self.assertTrue(State.load_selected_pet.is_background)
            self.assertTrue(State.fetch_tutor_clinical.is_background)
            with state_lock(state) as held:
                async def response(*args, **kwargs):
                    self.assertFalse(held[0])
                    return pet()
                detail.side_effect = response
                events = await consume(State.load_selected_pet.fn(state, state._pet_context_generation))
        self.assertEqual(state.selected_pet_id, '1')
        self.assertTrue(state.clinic_loading)
        self.assertFalse(state.is_loading_pet)
        self.assertEqual(len(events), 1)

    async def test_two_reads_overlap_and_navigation_is_free_without_duplicates(self):
        state = selected()
        calls = []
        started, release = asyncio.Event(), asyncio.Event()
        with state_lock(state) as held:
            async def response(method, group, endpoint, **kwargs):
                self.assertFalse(held[0])
                calls.append(endpoint)
                if len(calls) == 2:
                    started.set()
                await release.wait()
                return {} if endpoint.endswith('/historico') else []
            with patch(TARGET, side_effect=response):
                await consume(State.load_tutor_clinical.fn(state))
                generation = state._clinic_generation
                worker = asyncio.create_task(fetch(state))
                await asyncio.wait_for(started.wait(), 2)
                self.assertTrue(state.clinic_loading)
                for name in ('Vacinas', 'Medicamentos', 'Doenças', 'Consultas', 'Início'):
                    self.assertEqual(await consume(State.clinical_section.fn(state, name)), [])
                    self.assertEqual(state.active_section, name)
                await consume(State.load_tutor_clinical.fn(state))
                await State.fetch_tutor_clinical.fn(state, generation, False)
                self.assertEqual(state._clinic_generation, generation)
                self.assertEqual(len(calls), 2)
                release.set()
                await worker
        self.assertTrue(state.tutor_clinical_loaded)
        self.assertFalse(state.clinic_loading)
        self.assertFalse(any('/acessos' in route or '/auditoria' in route for route in calls))

    async def test_cache_boundary_and_manual_refresh(self):
        state = selected()
        with patch(TARGET, AsyncMock(side_effect=[{}, []])) as request, state_lock(state), patch('vet_tech.features.clinical.state.monotonic', return_value=100):
            await consume(State.load_tutor_clinical.fn(state))
            await fetch(state)
            self.assertEqual(request.await_count, 2)
        with patch('vet_tech.features.clinical.state.monotonic', return_value=159.9):
            self.assertEqual(await consume(State.clinical_section.fn(state, 'Vacinas')), [])
        with patch('vet_tech.features.clinical.state.monotonic', return_value=160):
            self.assertEqual(len(await consume(State.clinical_section.fn(state, 'Doenças'))), 1)
        self.assertFalse(state.tutor_clinical_loaded)
        self.assertTrue(state.clinic_loading)
        generation = state._clinic_generation
        await consume(State.load_tutor_clinical.fn(state))
        self.assertEqual(state._clinic_generation, generation)

    async def test_partial_failure_does_not_publish_empty_or_renew_cache_and_retry_works(self):
        for status in (None, 429, 503):
            state = selected()
            with self.subTest(status=status), state_lock(state):
                with patch(TARGET, AsyncMock(side_effect=[{'vacinas': [{'id': 9}]}, XanoRequestError('Falha', status_code=status)])):
                    await consume(State.load_tutor_clinical.fn(state))
                    await fetch(state)
                self.assertFalse(state.clinic_loading)
                self.assertFalse(state.tutor_clinical_loaded)
                self.assertEqual(state._tutor_loaded_at, 0)
                self.assertEqual(state.history_rows, {})
                self.assertEqual(state.selected_pet_id, '1')
                self.assertEqual(state.clinic_message, 'Falha')
                with patch(TARGET, AsyncMock(side_effect=[{}, []])):
                    await consume(State.load_tutor_clinical.fn(state))
                    await fetch(state)
                self.assertTrue(state.tutor_clinical_loaded)
                self.assertEqual(state.clinic_message, '')

    async def test_access_denial_wins_over_partial_success(self):
        for status in (401, 403, 404):
            state = selected()
            with self.subTest(status=status), state_lock(state), patch(TARGET, AsyncMock(side_effect=[{'vacinas': [{'id': 9}]}, XanoRequestError('Negado', status_code=status)])):
                await consume(State.load_tutor_clinical.fn(state))
                await fetch(state)
            self.assertFalse(state.selected_pet_id)
            self.assertFalse(state.tutor_clinical_loaded)
            self.assertFalse(state.clinic_loading)
            self.assertEqual(state.history_rows, {})

    async def test_old_success_and_error_do_not_touch_new_context(self):
        for action in ('switch', 'switch-back', 'close', 'logout', 'new-session'):
            for fail in (False, True):
                state = selected()
                started, release = asyncio.Event(), asyncio.Event()
                async def response(*args, **kwargs):
                    started.set()
                    await release.wait()
                    if fail:
                        raise XanoRequestError('Old error', status_code=401)
                    return {} if args[2].endswith('/historico') else []
                with self.subTest(action=action, fail=fail), state_lock(state), patch(TARGET, side_effect=response):
                    await consume(State.load_tutor_clinical.fn(state))
                    worker = asyncio.create_task(fetch(state))
                    await started.wait()
                    if action == 'logout':
                        await State.logout.fn(state)
                    else:
                        state._clear_pet_context()
                        if action in ('switch', 'switch-back', 'new-session'):
                            state.pet_target_id = '2' if action == 'switch' else '1'
                            state.selected_pet = {'id': state.pet_target_id}
                            state.clinic_loading = True
                        if action == 'new-session':
                            state._session_generation += 1
                            state._auth_token = 'new-session'
                    expected = (state.selected_pet_id, state.clinic_loading, state.is_authenticated)
                    release.set()
                    await worker
                    self.assertEqual((state.selected_pet_id, state.clinic_loading, state.is_authenticated), expected)
                    self.assertEqual(state.history_rows, {})

    async def test_auxiliary_is_explicit_and_error_preserves_clinical(self):
        state = selected()
        state.tutor_clinical_loaded = True
        state._tutor_loaded_at = time.monotonic()
        state.history_rows = {'vacinas': [{'id': '9'}]}
        with patch(TARGET, AsyncMock(side_effect=XanoRequestError('Falha auxiliar'))) as request, state_lock(state):
            event = State.load_tutor_auxiliary.fn(state, False)
            self.assertIsNotNone(event)
            request.assert_not_awaited()
            await State.fetch_tutor_auxiliary.fn(state, state._auxiliary_generation)
        self.assertTrue(state.tutor_clinical_loaded)
        self.assertEqual(state.history_rows['vacinas'][0]['id'], '9')
        self.assertFalse(state.auxiliary_loading)
        self.assertEqual(state.auxiliary_message, 'Falha auxiliar')
        with patch(TARGET, AsyncMock(return_value=[])) as request, state_lock(state):
            State.load_tutor_auxiliary.fn(state, True)
            await State.fetch_tutor_auxiliary.fn(state, state._auxiliary_generation)
            self.assertEqual(request.await_count, 2)
        self.assertTrue(state.auxiliary_loaded)
        self.assertIsNone(State.load_tutor_auxiliary.fn(state, False))

    async def test_confirmed_booking_refreshes_only_reservations_and_drops_old_read(self):
        for booking_pet in ('1', '2'):
            state = selected()
            state.tutor_clinical_loaded = True
            state._tutor_loaded_at = time.monotonic()
            state._tutor_history_loaded_at = state._tutor_loaded_at
            state.history_rows = {'vacinas': [{'id': '9'}]}
            state.booking_day, state.booking_time = '2030-01-01', '08:00'
            state.booking_pet, state.booking_professional, state.booking_reason = booking_pet, '3', 'Synthetic'
            generation = state._clinic_generation
            with self.subTest(booking_pet=booking_pet), patch(TARGET, AsyncMock(return_value={'id': 5})) as request:
                events = await consume(State.booking_submit.fn(state))
                request.assert_awaited_once()
            self.assertEqual(state.selected_pet_id, '1')
            if booking_pet == '1':
                self.assertGreater(state._clinic_generation, generation)
                self.assertTrue(state.clinic_loading)
                with patch(TARGET, AsyncMock(return_value=[])) as request, state_lock(state):
                    await State.fetch_tutor_clinical.fn(state, state._clinic_generation, True)
                    request.assert_awaited_once()
                    self.assertIn('tutor/consultas?', request.call_args.args[2])
                self.assertEqual(state.history_rows['vacinas'][0]['id'], '9')
            else:
                self.assertEqual(state._clinic_generation, generation)
                self.assertTrue(state.tutor_clinical_loaded)

    async def test_confirmed_consent_refreshes_auxiliary_without_history(self):
        state = selected()
        state.tutor_clinical_loaded = True
        state.auxiliary_loaded = True
        old_generation = state._auxiliary_generation
        with patch(TARGET, AsyncMock(return_value={})) as request:
            await consume(State.change_consent.fn(state, '4', 'revogado'))
            request.assert_awaited_once()
        self.assertGreater(state._auxiliary_generation, old_generation)
        self.assertTrue(state.auxiliary_loading)
        self.assertTrue(state.tutor_clinical_loaded)

    async def test_late_detail_does_not_start_clinical_of_previous_selection(self):
        state = session()
        state.species_options = [{'id': '1', 'nome': 'Cachorro'}]
        started, release = asyncio.Event(), asyncio.Event()
        async def response(*args, **kwargs):
            started.set()
            await release.wait()
            return pet()
        await consume(State.open_pet.fn(state, '1'))
        with patch('vet_tech.features.auth.state.xano_request', side_effect=response), state_lock(state):
            worker = asyncio.create_task(consume(State.load_selected_pet.fn(state, state._pet_context_generation)))
            await started.wait()
            await consume(State.open_pet.fn(state, '2'))
            release.set()
            self.assertEqual(await worker, [])
        self.assertEqual(state.pet_target_id, '2')
        self.assertTrue(state.is_loading_pet)
        self.assertFalse(state.clinic_loading)

    async def test_pet_picker_invalidates_pending_read(self):
        state = selected()
        state.clinic_loading = True
        generation = state._clinic_generation
        State.show_pet_picker.fn(state)
        self.assertGreater(state._clinic_generation, generation)
        self.assertFalse(state.selected_pet_id)
        self.assertFalse(state.clinic_loading)
        self.assertTrue(state.pet_picker_open)
