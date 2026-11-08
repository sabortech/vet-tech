import time
import unittest
from unittest.mock import AsyncMock, patch

from reflex.istate.data import ReflexURL, RouterData

from test_auth_state import make_state
import test_settings_state as settings_tests
from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import CLINICAL_SECTIONS
from vet_tech.features.settings.state import SettingsState


class UnifiedNavigationTests(unittest.IsolatedAsyncioTestCase):
    def test_switch_and_close_pet_redirect_to_meus_pets_and_clear_context(self):
        for handler in (State.show_pet_picker, State.close_pet):
            state = make_state()
            state.profile = 'tutor'
            state.selected_pet = {'id': '7'}
            state.pet_target_id = '7'
            generation = state._pet_context_generation
            event = handler.fn(state)
            destination = '/?selecionar=pet' if handler == State.show_pet_picker else '/'
            self.assertEqual(str(dict((str(k), v) for k, v in event.args)['path']), '"' + destination + '"')
            self.assertEqual(state.selected_pet_id, '')
            self.assertEqual(state.pet_target_id, '')
            self.assertGreater(state._pet_context_generation, generation)

    def test_pet_picker_mode_follows_url_instead_of_persistent_flag(self):
        state = make_state()
        state.pet_picker_open = False
        state.router = RouterData(url=ReflexURL('http://localhost/?selecionar=pet'))
        self.assertTrue(state.is_pet_picker_page)
        self.assertFalse(state.is_pet_form_page)
        state.pet_picker_open = True
        state.router = RouterData(url=ReflexURL('http://localhost/'))
        self.assertFalse(state.is_pet_picker_page)
        self.assertTrue(state.is_pet_form_page)
        state.router = RouterData(url=ReflexURL('http://localhost/prontuario'))
        self.assertFalse(state.is_pet_form_page)

    def test_settings_change_pet_waits_for_discard_and_rejects_veterinarian(self):
        settings, _ = settings_tests.SettingsTests().make()
        settings.nome = 'Rascunho'
        SettingsState.request_action.fn(settings, 'change_pet')
        self.assertTrue(settings.discard_open)
        self.assertEqual(settings._pending, 'change_pet')
        events = SettingsState.discard.fn(settings)
        self.assertEqual(events[-1], State.show_pet_picker)
        settings.account_profile = 'veterinario'
        self.assertIsNone(SettingsState.request_action.fn(settings, 'change_pet'))
        self.assertFalse(settings.discard_open)

    async def test_open_pet_starts_loading_sets_scope_and_redirects_to_dashboard(self):
        state = make_state()
        state._auth_token = 'synthetic'
        state.active_section = 'Vacinas'
        events = [event async for event in State.open_pet.fn(state, '7')]
        self.assertEqual(state.pet_target_id, '7')
        self.assertTrue(state.is_loading_pet)
        self.assertEqual(state.active_section, 'Início')
        scope_event = events[-1][-2]
        self.assertIn('set_dashboard_scope', str(scope_event.handler))
        self.assertEqual(str(dict((str(k), v) for k, v in scope_event.args)['value']), '"7"')
        redirect = events[-1][-1]
        self.assertEqual(str(dict((str(k), v) for k, v in redirect.args)['path']), '"/dashboard"')

    async def test_query_selects_section_without_network_and_keeps_pet_cache(self):
        state = make_state()
        state.profile = 'tutor'
        state._auth_token = 'synthetic'
        state.is_authenticated = True
        state.selected_pet = {'id': '7'}
        state.pet_target_id = '7'
        state.tutor_clinical_loaded = True
        state._tutor_loaded_at = time.monotonic()
        for key, section in CLINICAL_SECTIONS.items():
            state.router = RouterData(url=ReflexURL('http://localhost/prontuario?secao=' + key))
            with patch('vet_tech.features.clinical.state.xano_request', AsyncMock()) as request:
                event = State.enter_clinical_page.fn(state)
            self.assertIsNone(event)
            request.assert_not_awaited()
            self.assertEqual(state.active_section, section)
            self.assertEqual(state.clinical_menu_item, 'prontuario' if key == 'inicio' else key)
            self.assertEqual(state.selected_pet_id, '7')
        state.router = RouterData(url=ReflexURL('http://localhost/prontuario?secao=invalid'))
        State.enter_clinical_page.fn(state)
        self.assertEqual(state.active_section, 'Início')

    async def test_no_pet_preserves_section_intent_without_loading(self):
        state = make_state()
        state.is_authenticated = True
        state.profile = 'tutor'
        state._auth_token = 'synthetic'
        state.router = RouterData(url=ReflexURL('http://localhost/prontuario?secao=vacinas'))
        self.assertIsNone(State.enter_clinical_page.fn(state))
        self.assertEqual(state.active_section, 'Vacinas')
        self.assertFalse(state.selected_pet_id)
        self.assertFalse(state.clinic_loading)
        state._start_pet_selection('7')
        self.assertEqual(state.active_section, 'Vacinas')
        self.assertTrue(state.is_loading_pet)

    async def test_unauthenticated_clinical_entry_redirects_without_api(self):
        state = make_state()
        with patch('vet_tech.features.clinical.state.xano_request', AsyncMock()) as request:
            event = State.enter_clinical_page.fn(state)
        self.assertIsNotNone(event)
        request.assert_not_awaited()

    def test_settings_guard_keeps_exact_allowed_destination_even_before_input_delta(self):
        state, _ = settings_tests.SettingsTests().make()
        destination = '/prontuario?secao=vacinas'
        self.assertFalse(state.dirty)
        SettingsState.request_navigation.fn(state, destination)
        self.assertTrue(state.discard_open)
        self.assertEqual(state._pending, destination)
        SettingsState.keep_editing.fn(state)
        self.assertFalse(state.discard_open)
        self.assertEqual(state._pending, '')
        state.nome = 'Alterado'
        SettingsState.request_navigation.fn(state, destination)
        events = SettingsState.discard.fn(state)
        self.assertEqual(str(dict((str(k), v) for k, v in events[-1].args)['path']), '"' + destination + '"')
        self.assertFalse(state.dirty)

    def test_invalid_destination_and_saving_never_navigate(self):
        for target in ('https://example.invalid', '//example.invalid', '/prontuario?secao=invalid', '/exames'):
            state, _ = settings_tests.SettingsTests().make()
            self.assertIsNone(SettingsState.request_navigation.fn(state, target))
            self.assertFalse(state.discard_open)
            self.assertEqual(state._pending, '')
            self.assertIsNone(SettingsState.request_action.fn(state, target))
        state, _ = settings_tests.SettingsTests().make()
        state.saving = True
        self.assertIsNone(SettingsState.request_navigation.fn(state, '/prontuario'))
        self.assertFalse(state.discard_open)

    def test_modal_open_and_close_do_not_redirect_or_clear_selection(self):
        state = make_state()
        state.profile = 'tutor'
        state.selected_pet = {'id': '7'}
        state.active_section = 'Vacinas'
        for opened in (True, False):
            event = State.set_pet_modal.fn(state, opened)
            self.assertEqual(state.pet_modal_open, opened)
            self.assertEqual(state.selected_pet_id, '7')
            self.assertEqual(state.active_section, 'Vacinas')
            self.assertNotIn('redirect', str(event))
