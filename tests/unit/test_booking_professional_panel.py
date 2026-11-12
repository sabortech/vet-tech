"""First-step selections keep each consultation bound to its own pet and doctor."""
import unittest
from unittest.mock import AsyncMock, patch
from test_clinical_state import session, consume, TARGET
from vet_tech.features.auth.state import State


class BookingProfessionalPanelTests(unittest.IsolatedAsyncioTestCase):
    def prepare(self):
        state = session()
        state.pets = [{'id': '1', 'nome': 'Jessy'}, {'id': '2', 'nome': 'Max'}]
        state.booking_open = True
        state.booking_day, state.booking_time = '2099-04-03', '08:00'
        return state

    async def test_first_step_requires_current_pet_and_doctor_and_shows_names(self):
        state = self.prepare()
        State.booking_next.fn(state)
        self.assertEqual(state.booking_step, 1)
        with patch(TARGET, AsyncMock(return_value=[{'id': 3, 'nome': 'Dra. Ana'}])):
            await State.booking_choose_pet.fn(state, '1')
        State.set_booking_professional.fn(state, '99')
        self.assertEqual(state.booking_professional, '')
        State.booking_next.fn(state)
        self.assertEqual(state.booking_step, 1)
        State.set_booking_professional.fn(state, '3')
        State.booking_next.fn(state)
        self.assertEqual(state.booking_step, 2)
        self.assertEqual(state.booking_pet_name, 'Jessy')
        self.assertEqual(state.booking_professional_name, 'Dra. Ana')
        State.booking_back.fn(state)
        self.assertEqual(state.booking_professional, '3')

    async def test_pet_change_clears_previous_doctor_and_empty_catalog_blocks_advance(self):
        state = self.prepare()
        state.booking_professional = '3'
        with patch(TARGET, AsyncMock(return_value=[])) as request:
            await State.booking_choose_pet.fn(state, '2')
        self.assertIn('pet_id=2', request.await_args.args[2])
        self.assertEqual(state.booking_professional, '')
        self.assertIn('Nenhum profissional', state.booking_message)
        State.booking_next.fn(state)
        self.assertEqual(state.booking_step, 1)

    async def test_each_booking_sends_its_selected_pet_and_doctor(self):
        submitted = []
        for pet_id, doctor_id in [('1', '3'), ('2', '4')]:
            state = self.prepare()
            with patch(TARGET, AsyncMock(return_value=[{'id': int(doctor_id), 'nome': 'Médico ' + doctor_id}])):
                await State.booking_choose_pet.fn(state, pet_id)
            State.set_booking_professional.fn(state, doctor_id)
            State.booking_next.fn(state)
            state.booking_reason = 'Consulta de rotina'
            with patch(TARGET, AsyncMock(return_value={'id': 42})) as request:
                await consume(State.booking_submit.fn(state))
            submitted.append(request.await_args.kwargs['json_payload']['payload'])
        self.assertEqual([(row['pet_id'], row['veterinario_id']) for row in submitted], [('1', '3'), ('2', '4')])
        self.assertNotEqual(submitted[0]['operacao'], submitted[1]['operacao'])
