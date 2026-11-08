import asyncio
from time import perf_counter
import unittest
from unittest.mock import AsyncMock, patch

from reflex.istate.data import ReflexURL, RouterData

from test_auth_state import make_state
from test_pet_clinical_loading import state_lock
from vet_tech.features.auth.state import State


def performance_state(route='/dashboard'):
    state = make_state()
    state.is_authenticated = True
    state.profile = 'tutor'
    state._auth_token = 'synthetic-session'
    state.router = RouterData(url=ReflexURL('http://localhost' + route))
    state.pets = [{'id': '1', 'nome': 'Pet'}]
    state.species_options = [{'id': '1', 'nome': 'Cachorro'}]
    return state


async def measure_catalog_loading():
    """Compare six sequential catalog waits to the actual bounded loader."""
    state = performance_state()
    state.species_options = [{'id': str(i), 'nome': 'Espécie ' + str(i)} for i in range(1, 7)]
    rows = [{'id': i, 'nome': 'Pet ' + str(i), 'especie_id': i, 'raca_id': i} for i in range(1, 7)]
    active = peak = 0
    delay = .06

    async def response(method, group, endpoint, **kwargs):
        nonlocal active, peak
        if endpoint == 'pets':
            return rows
        species = endpoint.rsplit('=', 1)[-1]
        active += 1
        peak = max(peak, active)
        try:
            await asyncio.sleep(delay)
            return [{'id': int(species), 'nome': 'Raça ' + species}]
        finally:
            active -= 1

    with patch('vet_tech.features.auth.state.xano_request', side_effect=response):
        started = perf_counter()
        for species in range(1, 7):
            await state._load_breeds(str(species), token='synthetic-session')
        sequential = perf_counter() - started
        peak = 0
        started = perf_counter()
        await state._load_pets()
        bounded = perf_counter() - started
    return {'sequential_ms': round(sequential*1000, 1), 'bounded_ms': round(bounded*1000, 1),
            'peak_concurrency': peak, 'pet_count': len(state.pets)}


class InterfacePerformanceTests(unittest.IsolatedAsyncioTestCase):
    async def test_dashboard_detail_does_not_prefetch_clinical_history(self):
        state = performance_state()
        state._start_pet_selection('1')
        with patch('vet_tech.features.auth.state.xano_request', AsyncMock(return_value={'id': 1, 'nome': 'Pet', 'especie_id': 1})), state_lock(state):
            events = [event async for event in State.load_selected_pet.fn(state, state._pet_context_generation)]
        self.assertEqual(events, [])
        self.assertFalse(state.clinic_loading)
        self.assertEqual(state.selected_pet_id, '1')
        state.router = RouterData(url=ReflexURL('http://localhost/prontuario?secao=vacinas'))
        event = State.enter_clinical_page.fn(state)
        self.assertIsNotNone(event)
        self.assertTrue(state.clinic_loading)
        calls = []

        async def response(method, group, endpoint, **kwargs):
            calls.append(endpoint)
            return {} if endpoint.endswith('/historico') else []

        with patch('vet_tech.features.clinical.state.xano_request', side_effect=response), state_lock(state):
            await State.fetch_tutor_clinical.fn(state, state._clinic_generation, False)
        self.assertEqual(len(calls), 2)
        self.assertTrue(state.tutor_clinical_loaded)
        self.assertIsNone(State.enter_clinical_page.fn(state))

    async def test_enter_clinical_while_detail_is_pending_still_schedules_history(self):
        state = performance_state()
        state._start_pet_selection('1')
        entered, release = asyncio.Event(), asyncio.Event()

        async def response(*args, **kwargs):
            entered.set()
            await release.wait()
            return {'id': 1, 'nome': 'Pet', 'especie_id': 1}

        async def run_detail():
            return [event async for event in State.load_selected_pet.fn(state, state._pet_context_generation)]

        with patch('vet_tech.features.auth.state.xano_request', side_effect=response), state_lock(state):
            worker = asyncio.create_task(run_detail())
            await entered.wait()
            state.router = RouterData(url=ReflexURL('http://localhost/prontuario'))
            self.assertIsNone(State.enter_clinical_page.fn(state))
            release.set()
            events = await worker
        self.assertEqual(len(events), 1)
        self.assertTrue(state.clinic_loading)

    async def test_breed_catalogs_overlap_with_at_most_four_requests(self):
        result = await measure_catalog_loading()
        self.assertEqual(result['peak_concurrency'], 4)
        self.assertEqual(result['pet_count'], 6)
        self.assertLess(result['bounded_ms'], result['sequential_ms'] * .85)
