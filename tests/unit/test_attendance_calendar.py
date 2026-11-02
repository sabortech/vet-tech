"""Clinical calendar selection stays local and targets stable draft fields."""
import unittest
from unittest.mock import AsyncMock, patch
from test_clinical_state import session
from vet_tech.features.auth.state import State
from vet_tech.features.clinical.state import CLINICAL_DATE_FIELDS


class AttendanceCalendarTests(unittest.TestCase):
    def setUp(self):
        self.state = session('veterinario')
        self.state.clinical_id = '43'
        self.state.clinical_status = 'em_atendimento'
        self.state.clinical_date = '2028-02-21'

    def test_navigation_and_cancel_do_not_change_draft_or_agenda_or_request_http(self):
        s = self.state
        s.agenda_day = '2030-01-05'
        s.agenda_calendar_month = '2030-01'
        with patch('vet_tech.features.clinical.state.xano_request', new_callable=AsyncMock) as request:
            State.clinical_calendar_show.fn(s, 'data_atendimento')
            self.assertEqual(s.clinical_calendar_month, '2028-02')
            State.clinical_calendar_choose_year.fn(s, '2029')
            State.clinical_calendar_choose_month.fn(s, 'Dezembro')
            State.clinical_calendar_shift.fn(s, 1)
            State.clinical_calendar_set_open.fn(s, False)
            self.assertEqual(s.clinical_calendar_month, '2030-01')
            self.assertEqual(s.clinical_date, '2028-02-21')
            self.assertFalse(s.clinical_dirty)
            self.assertEqual(s.agenda_day, '2030-01-05')
            self.assertEqual(s.agenda_calendar_month, '2030-01')
            request.assert_not_called()

    def test_header_selection_and_clearing_use_the_correct_field(self):
        s = self.state
        State.clinical_calendar_show.fn(s, 'retorno_previsto')
        State.clinical_calendar_choose_day.fn(s, '2028-03-05')
        self.assertEqual(s.clinical_return, '2028-03-05')
        self.assertEqual(s.clinical_date, '2028-02-21')
        self.assertTrue(s.clinical_dirty)
        self.assertFalse(s.clinical_calendar_open)
        State.clinical_calendar_show.fn(s, 'retorno_previsto')
        State.clinical_calendar_choose_day.fn(s, '')
        self.assertEqual(s.clinical_return, '')

    def test_all_line_date_fields_target_the_stable_line_id(self):
        s = self.state
        for group, fields in CLINICAL_DATE_FIELDS.items():
            if not group:
                continue
            State.clinical_add_line.fn(s, group)
            State.clinical_add_line.fn(s, group)
            target = s.clinical_lines[group][1]['linha_id']
            for field in fields:
                State.clinical_calendar_show.fn(s, field, group, target)
                if len(s.clinical_lines[group]) > 1:
                    State.clinical_remove_line.fn(s, group, s.clinical_lines[group][0]['linha_id'])
                State.clinical_calendar_choose_day.fn(s, '2028-02-29')
                self.assertEqual(s.clinical_lines[group][0]['linha_id'], target)
                self.assertEqual(s.clinical_lines[group][0][field], '2028-02-29')
            self.assertEqual(s.clinical_date, '2028-02-21')

    def test_invalid_dates_and_fields_are_rejected_and_leap_day_is_correct(self):
        s = self.state
        State.clinical_calendar_show.fn(s, 'data_atendimento')
        self.assertEqual(len(s.clinical_calendar_days), 42)
        self.assertIn('2028-02-29', [d['date'] for d in s.clinical_calendar_days])
        State.clinical_calendar_choose_year.fn(s, '2029')
        self.assertNotIn('2029-02-29', [d['date'] for d in s.clinical_calendar_days])
        for value in ('2029-02-29', '2028-13-10', '20280201', 'invalid'):
            State.clinical_calendar_choose_day.fn(s, value)
            self.assertTrue(s.clinical_calendar_open)
            self.assertEqual(s.clinical_date, '2028-02-21')
        State.clinical_calendar_show.fn(s, 'diagnostico')
        self.assertFalse(s.clinical_calendar_open)

    def test_locks_finished_consultations_and_removed_targets_cannot_be_modified(self):
        s = self.state
        for attribute, blocked in [('clinic_busy', True), ('_save_uncertain', True), ('clinical_status', 'finalizada'), ('profile', 'tutor')]:
            original = getattr(s, attribute)
            setattr(s, attribute, blocked)
            State.clinical_calendar_show.fn(s, 'data_atendimento')
            self.assertFalse(s.clinical_calendar_open)
            setattr(s, attribute, original)
        State.clinical_add_line.fn(s, 'vacinas')
        line = s.clinical_lines['vacinas'][0]['linha_id']
        State.clinical_calendar_show.fn(s, 'data_aplicacao', 'vacinas', line)
        State.clinical_remove_line.fn(s, 'vacinas', line)
        s.clinical_dirty = False
        State.clinical_calendar_choose_day.fn(s, '2028-01-01')
        self.assertFalse(s.clinical_dirty)
        self.assertEqual(s.clinical_lines['vacinas'], [])

    def test_session_cleanup_and_year_boundaries(self):
        s = self.state
        State.clinical_calendar_show.fn(s, 'data_atendimento')
        for month, direction in [('0001-01', -1), ('9999-12', 1)]:
            s.clinical_calendar_month = month
            State.clinical_calendar_shift.fn(s, direction)
            self.assertEqual(s.clinical_calendar_month, month)
            self.assertEqual(len(s.clinical_calendar_days), 42)
        s._clear_clinical_session()
        self.assertFalse(s.clinical_calendar_open)
        self.assertEqual(s.clinical_calendar_field, '')
