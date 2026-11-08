"""Shared calendar appearance retains independent tutor draft rules."""
import unittest
from unittest.mock import AsyncMock, patch
from test_auth_state import make_state
from vet_tech.features.auth.state import State


def tutor():
    s = make_state()
    s.is_authenticated = True
    s.profile = 'tutor'
    s._auth_token = 'synthetic'
    return s


class TutorCalendarTests(unittest.TestCase):
    def test_booking_grid_and_navigation_preserve_selected_date(self):
        s = tutor()
        s.booking_open = True
        s.booking_month = '2026-11'
        s.booking_day = '2026-11-20'
        with patch('vet_tech.features.clinical.state.today', return_value='2026-11-07'), patch('vet_tech.features.clinical.state.xano_request', new_callable=AsyncMock) as remote:
            self.assertEqual(len(s.booking_days), 42)
            rows = {d['date']: d for d in s.booking_days if d['date']}
            self.assertEqual(rows['2026-11-06']['disabled'], 'sim')
            self.assertEqual(rows['2026-11-07']['today'], 'sim')
            self.assertEqual(rows['2026-11-20']['selected'], 'sim')
            State.booking_choose_year.fn(s, '2028')
            State.booking_choose_month.fn(s, 'Fevereiro')
            self.assertIn('2028-02-29', [d['date'] for d in s.booking_days])
            State.booking_shift_month.fn(s, 1)
            self.assertEqual(s.booking_month, '2028-03')
            self.assertEqual(s.booking_day, '2026-11-20')
            remote.assert_not_called()

    def test_booking_rejects_past_invalid_and_changes_while_locked(self):
        s = tutor()
        s.booking_open = True
        with patch('vet_tech.features.clinical.state.today', return_value='2026-11-07'):
            for value in ('2026-11-06', '2026-02-30', 'invalid', '', '20261108'):
                State.booking_choose_day.fn(s, value)
                self.assertEqual(s.booking_day, '')
            State.booking_choose_day.fn(s, '2026-11-08')
            self.assertEqual(s.booking_day, '2026-11-08')
            self.assertTrue(s.booking_open)
            s.booking_month = '2026-11'
            for attr in ('booking_busy', '_booking_uncertain'):
                setattr(s, attr, True)
                State.booking_choose_day.fn(s, '2026-11-10')
                State.booking_shift_month.fn(s, 1)
                State.booking_choose_year.fn(s, '2027')
                State.booking_next.fn(s)
                self.assertEqual(s.booking_month, '2026-11')
                self.assertEqual(s.booking_day, '2026-11-08')
                self.assertEqual(s.booking_step, 1)
                setattr(s, attr, False)

    def test_booking_continues_and_back_preserves_day(self):
        s = tutor()
        s.booking_open = True
        s.booking_day = '2099-04-03'
        for hour in ('07:59', '17:01', ''):
            s.booking_time = hour
            State.booking_next.fn(s)
            self.assertEqual(s.booking_step, 1)
        s.booking_time = '08:00'
        State.booking_next.fn(s)
        self.assertEqual(s.booking_step, 2)
        State.booking_back.fn(s)
        self.assertEqual(s.booking_step, 1)
        self.assertEqual(s.booking_day, '2099-04-03')

    def test_birth_grid_rejects_future_and_accepts_leap_day(self):
        s = tutor()
        s.pet_name = 'Pet de teste'
        with patch('vet_tech.features.auth.state.today', return_value='2026-11-07'):
            State.birth_calendar_set_open.fn(s, True)
            self.assertEqual(s.birth_calendar_month, '2026-11')
            rows = {d['date']: d for d in s.birth_calendar_days if d['date']}
            self.assertEqual(rows['2026-11-08']['disabled'], 'sim')
            self.assertEqual(rows['2026-11-07']['disabled'], 'nao')
            for value in ('2026-11-08', '2025-02-29', 'bad', '20260203'):
                State.birth_calendar_choose_day.fn(s, value)
                self.assertEqual(s.pet_birth_date, '')
                self.assertTrue(s.birth_calendar_open)
            State.birth_calendar_choose_year.fn(s, '2024')
            State.birth_calendar_choose_month.fn(s, 'Fevereiro')
            State.birth_calendar_choose_day.fn(s, '2024-02-29')
            self.assertEqual(s.pet_birth_date, '2024-02-29')
            self.assertEqual(s.birth_date_label, '29/02/2024')
            self.assertFalse(s.birth_calendar_open)
            self.assertEqual(s.pet_name, 'Pet de teste')

    def test_birth_navigation_into_future_does_not_set_a_date(self):
        s = tutor()
        with patch('vet_tech.features.auth.state.today', return_value='2026-11-07'):
            State.birth_calendar_set_open.fn(s, True)
            State.birth_calendar_choose_year.fn(s, '2027')
            self.assertEqual(s.birth_calendar_year, '2027')
            self.assertTrue(all(day['disabled'] == 'sim' for day in s.birth_calendar_days if day['date']))
            self.assertEqual(s.pet_birth_date, '')

    def test_birth_cancel_clear_busy_and_logout(self):
        s = tutor()
        s.pet_birth_date = '2024-02-29'
        State.birth_calendar_set_open.fn(s, True)
        State.birth_calendar_shift.fn(s, 1)
        State.birth_calendar_set_open.fn(s, False)
        self.assertEqual(s.pet_birth_date, '2024-02-29')
        State.birth_calendar_set_open.fn(s, True)
        s.is_busy = True
        State.birth_calendar_choose_day.fn(s, '')
        self.assertEqual(s.pet_birth_date, '2024-02-29')
        s.is_busy = False
        State.birth_calendar_choose_day.fn(s, '')
        self.assertEqual(s.pet_birth_date, '')
        State.birth_calendar_set_open.fn(s, True)
        s._clear_session()
        self.assertFalse(s.birth_calendar_open)
        self.assertEqual(s.birth_calendar_month, '')

    def test_birth_cannot_open_without_authenticated_tutor(self):
        for profile, authenticated in (('veterinario', True), ('tutor', False)):
            s = tutor()
            s.profile, s.is_authenticated = profile, authenticated
            State.birth_calendar_set_open.fn(s, True)
            self.assertFalse(s.birth_calendar_open)
