import unittest
from unittest.mock import patch

from test_auth_state import make_state
from vet_tech.features.clinical.state import RECORD_BACKGROUNDS


class RecordBackgroundTests(unittest.TestCase):
    def test_variety_then_stability_when_reordered_and_extended(self):
        state = make_state()
        rows = [{'id': str(i), 'nome': 'Registro ' + str(i)} for i in range(1, len(RECORD_BACKGROUNDS)+1)]
        with patch('vet_tech.features.clinical.state.choice', side_effect=lambda options: options[0]):
            first = state._with_record_backgrounds({'vacinas': rows}, '1')['vacinas']
            self.assertEqual(len({r['fundo_card'] for r in first}), len(RECORD_BACKGROUNDS))
            again = state._with_record_backgrounds({'vacinas': list(reversed(rows)) + [{'id': 'novo'}]}, '1')['vacinas']
        originals = {r['id']: r['fundo_card'] for r in first}
        self.assertTrue(all(r['fundo_card'] == originals[r['id']] for r in again if r['id'] in originals))
        self.assertTrue(all('fundo_card' not in r for r in rows))
        self.assertIn(again[-1]['fundo_card'], RECORD_BACKGROUNDS)

    def test_same_id_is_isolated_by_pet_and_group(self):
        state = make_state()
        with patch('vet_tech.features.clinical.state.choice', side_effect=lambda options: options[0]):
            state._with_record_backgrounds({'vacinas': [{'id': '1'}], 'medicamentos': [{'id': '1'}]}, '1')
            state._with_record_backgrounds({'vacinas': [{'id': '1'}]}, '2')
        self.assertEqual(set(state._record_background_choices), {'1:vacinas:1', '1:medicamentos:1', '2:vacinas:1'})
        state._clear_clinical_session()
        self.assertEqual(state._record_background_choices, {})

    def test_legacy_rows_remain_stable_without_mutating_original(self):
        state = make_state()
        history = {'medicamentos': [{'nome': 'Vitamina D', 'dose_legivel': '0 mg'}], 'doencas': [{'nome': 'Registro'}]}
        first = state._with_record_backgrounds(history, '1')
        again = state._with_record_backgrounds(history, '1')
        self.assertEqual(first, again)
        self.assertIn(first['doencas'][0]['fundo_card'], RECORD_BACKGROUNDS)
        self.assertNotIn('fundo_card', history['doencas'][0])
        self.assertEqual(first['medicamentos'][0]['dose_legivel'], '0 mg')

    def test_four_backgrounds_in_all_illustrated_categories_and_shared_consultation(self):
        state = make_state()
        groups = ('vacinas', 'medicamentos', 'doencas', 'diagnosticos', 'exames', 'consultas')
        history = {group: [{'id': str(i)} for i in range(1, 5)] for group in groups}
        with patch('vet_tech.features.clinical.state.choice', side_effect=lambda options: options[0]):
            projected = state._with_record_backgrounds(history, '1')
            for group in groups:
                self.assertEqual({row['fundo_card'] for row in projected[group]}, set(RECORD_BACKGROUNDS))
            listing = state._with_record_backgrounds({'consultas': [{'id': '1'}]}, '1')
            self.assertEqual(listing['consultas'][0]['fundo_card'], projected['consultas'][0]['fundo_card'])
        self.assertIn('/optimized/fundinho.webp', RECORD_BACKGROUNDS)
