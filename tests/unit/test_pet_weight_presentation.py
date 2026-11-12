"""Both patient summaries use Kg without changing the stored measurement."""
import unittest
from datetime import date
from vet_tech.features.clinical.state import pet_summary
from vet_tech.features.dashboard.state import project_pet


class PetWeightPresentationTests(unittest.TestCase):
    def test_dashboard_and_record_preserve_zero_decimals_and_missing_weights(self):
        for value, expected in [(0, '0 Kg'), (5, '5 Kg'), (4.2, '4.2 Kg'),
                                ('12', '12 Kg'), (None, None), ('', None)]:
            with self.subTest(value=value):
                row = {'id': 1, 'peso_atual': value, 'consultas': [], 'vacinas': [], 'exames': []}
                clinical = pet_summary(row)
                dashboard = project_pet(row, date(2026, 11, 11))
                self.assertEqual(clinical['peso'], expected or 'Não informado')
                self.assertEqual(dashboard['peso'], expected or '')
                self.assertEqual(row['peso_atual'], value)
