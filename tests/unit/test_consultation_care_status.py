"""Care colors describe recorded facts and prescription periods, never adherence."""
from datetime import date
import unittest

from vet_tech.features.clinical.state import care_status


class CareStatusTests(unittest.TestCase):
    def classify(self, group, **row):
        return care_status(row, group, date(2026, 11, 11))

    def test_vaccine_application_and_next_date(self):
        for next_dose, tone in [('2026-11-10', 'red'), ('2026-11-11', 'yellow'), ('2026-11-18', 'yellow'), ('2026-11-19', 'green')]:
            item = self.classify('vacinas', data_aplicacao='2026-11-01', data_prox_dose=next_dose)
            self.assertEqual(item['care_tone'], tone)
            self.assertIn('Aplicada', item['care_label'])
        self.assertEqual(self.classify('vacinas')['care_tone'], 'neutral')
        self.assertNotIn('Aplicada', self.classify('vacinas', data_aplicacao='2026-12-01')['care_label'])

    def test_medication_period_does_not_confirm_taken_doses(self):
        for start, end, tone in [('2026-11-12', '2026-11-20', 'red'), ('2026-11-01', '2026-11-11', 'yellow'), ('2026-11-01', '2026-11-10', 'green')]:
            item = self.classify('medicamentos', data_inicio=start, data_fim=end)
            self.assertEqual(item['care_tone'], tone)
            self.assertNotIn('tomad', item['care_label'])
        self.assertEqual(self.classify('medicamentos', data_inicio='2026-11-01', tipo='continuo')['care_tone'], 'yellow')
        for row in ({}, {'data_inicio':'invalid'}, {'data_inicio':'2026-11-11', 'data_fim':'2026-11-01'}):
            self.assertEqual(self.classify('medicamentos', **row)['care_tone'], 'neutral')

    def test_recorded_disease_and_exam_states(self):
        for state, tone in [('ativa','red'), ('em_tratamento','yellow'), ('controlada','yellow'), ('curada','green'), ('unknown','neutral')]:
            self.assertEqual(self.classify('diagnosticos', estado=state)['care_tone'], tone)
        for state, tone in [('solicitado','red'), ('realizado','green'), ('unknown','neutral')]:
            self.assertEqual(self.classify('exames', status=state)['care_tone'], tone)
