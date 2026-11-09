"""Save notifications must follow confirmed writes for the current consultation."""
import unittest
from unittest.mock import AsyncMock, patch
from reflex.istate.data import RouterData, PageData
from test_clinical_state import session, consume, TARGET
from vet_tech.features.auth.state import State
from vet_tech.features.clinical.state import attendance_saved_toast
from vet_tech.shared.xano_client import XanoRequestError

def flattened(events):
    return [item for event in events for item in (event if isinstance(event, list) else [event])]


NOTIFY = 'vet_tech.features.clinical.state.attendance_saved_toast'


class AttendanceNotificationTests(unittest.IsolatedAsyncioTestCase):
    def make_attendance(self):
        state = session('veterinario')
        state.clinical_id = '43'
        state.clinical_status = 'em_atendimento'
        state.clinical_version = 1
        state.clinical_dirty = True
        state.clinical_agenda_day = '2026-11-03'
        state.clinical_date = '2026-11-02'
        return state

    async def test_loading_keeps_scheduled_business_day_separate_from_clinical_date(self):
        state = self.make_attendance()
        state.router = RouterData(_page=PageData(params={'consulta_id': '43'}))
        row = {'id':43, 'pet_id':1, 'status':'em_atendimento', 'versao':1,
               'agendada_para':'2026-11-04T01:00:00Z',
               'rascunho':{'data_atendimento':'2026-11-02'}}
        with patch(TARGET, AsyncMock(side_effect=[{'consulta':row, 'pet':{'nome':'Jessy'}}, []])):
            await consume(State.load_attendance.fn(state))
        self.assertEqual(state.clinical_agenda_day, '2026-11-03')
        self.assertEqual(state.clinical_date, '2026-11-02')
        state._clear_clinical_session()
        self.assertEqual(state.clinical_agenda_day, '')

    async def test_confirmed_save_and_finalize_emit_one_matching_notification(self):
        for finalize in (False, True):
            state = self.make_attendance()
            status = 'finalizada' if finalize else 'em_atendimento'
            with patch(TARGET, AsyncMock(return_value={'versao': 2, 'status': status})), patch(NOTIFY, return_value='success-event') as notify:
                events = await consume(State.save_attendance.fn(state, finalize))
            notify.assert_called_once_with(finalize)
            self.assertEqual(flattened(events).count('success-event'), 1)
            self.assertFalse(state.clinical_dirty)
            self.assertFalse(state.clinic_busy)
            if finalize:
                self.assertEqual(state.clinical_status, 'finalizada')
                self.assertNotIn('redirect', str(events))
            else:
                self.assertNotIn('/?secao=horarios', str(events))

    async def test_finalization_updates_only_matching_card_and_removes_pending(self):
        state = self.make_attendance()
        state.vet_section = 'Consultas'
        state.agenda_page = 3
        state.agenda_rows = [{'id': '43', 'status': 'em_atendimento'}, {'id': '44', 'status': 'agendada'}]
        state.upcoming_rows = [{'id': '43'}, {'id': '44'}]
        with patch(TARGET, AsyncMock(return_value={'versao': 2, 'status': 'finalizada'})):
            await consume(State.save_attendance.fn(state, True))
        self.assertEqual(state.agenda_rows[0]['status_label'], 'Concluída')
        self.assertEqual(state.agenda_rows[0]['status'], 'finalizada')
        self.assertEqual(state.agenda_rows[1]['status'], 'agendada')
        self.assertEqual(state.upcoming_rows, [{'id': '44'}])
        self.assertEqual(state.agenda_page, 3)

    def test_notifications_target_bottom_left(self):
        for finalized in (False, True):
            self.assertIn('bottom-left', str(attendance_saved_toast(finalized)))

    async def test_errors_never_emit_success(self):
        for status in (400, 403, 500, None):
            state = self.make_attendance()
            with patch(TARGET, AsyncMock(side_effect=XanoRequestError('Synthetic error', status_code=status))), patch(NOTIFY) as notify:
                await consume(State.save_attendance.fn(state, False))
            notify.assert_not_called()
            self.assertNotEqual(state.agenda_day, '2026-11-03')

    async def test_old_consultation_or_session_does_not_emit_success(self):
        for change_session in (False, True):
            state = self.make_attendance()
            async def request(*args, **kwargs):
                if change_session:
                    state._session_generation += 1
                else:
                    state.clinical_id = '44'
                return {'versao': 2, 'status': 'em_atendimento'}
            with patch(TARGET, side_effect=request), patch(NOTIFY) as notify:
                await consume(State.save_attendance.fn(state))
            notify.assert_not_called()
            self.assertNotEqual(state.agenda_day, '2026-11-03')

    async def test_reconciliation_notifies_confirmed_result_without_repeating_write(self):
        for finalized in (False, True):
            state = self.make_attendance()
            state._save_uncertain = True
            state._pending_version = 1
            state._pending_payload = state._clinical_payload()
            confirmed = {'status': 'finalizada' if finalized else 'em_atendimento', 'versao': 2, 'rascunho': state._pending_payload}
            with patch(TARGET, AsyncMock(return_value={'consulta': confirmed})) as request, patch(NOTIFY, return_value='success-event') as notify:
                events = await consume(State.save_attendance.fn(state, finalized))
            notify.assert_called_once_with(finalized)
            self.assertIn('success-event', flattened(events))
            self.assertEqual(request.call_count, 1)
            self.assertEqual(request.call_args.args[0], 'GET')
            if finalized:
                self.assertNotIn('redirect', str(events))
                self.assertEqual(state.clinical_status, 'finalizada')
            else:
                self.assertNotIn('/?secao=horarios', str(events))

    async def test_reconciliation_conflict_does_not_emit_success(self):
        state = self.make_attendance()
        state._save_uncertain = True
        state._pending_version = 1
        state._pending_payload = {'motivo': 'Local'}
        with patch(TARGET, AsyncMock(return_value={'consulta': {'status': 'em_atendimento', 'versao': 2, 'rascunho': {'motivo': 'Other'}}})), patch(NOTIFY) as notify:
            await consume(State.save_attendance.fn(state))
        notify.assert_not_called()
        self.assertTrue(state.clinical_dirty)
        self.assertNotEqual(state.agenda_day, '2026-11-03')
