"""Professional names survive clinical projections and appear in exported PDFs."""
import unittest
from io import BytesIO
from pypdf import PdfReader
from test_consultation_pdf import export_payload
from test_clinical_projections import execute
from vet_tech.features.clinical.state import cards
from vet_tech.features.clinical.consultation_pdf import map_consultation_document
from vet_tech.features.clinical.consultation_pdf_template import render_consultation_pdf


class VeterinarianDisplayNameTests(unittest.TestCase):
    def test_cards_keep_names_and_use_text_for_missing_names(self):
        rows = cards([{'veterinario_id': 3, 'veterinario_nome': name}
                      for name in ['Dra. Ana', None, '', '   ']])
        self.assertEqual([r['veterinario_nome'] for r in rows],
                         ['Dra. Ana'] + ['Nome não informado'] * 3)
        self.assertTrue(all(r['veterinario_id'] == '3' for r in rows))

    def test_history_preserves_evolution_professional_name_in_condition(self):
        rows = {'consultations': [{'id': 1, 'status': 'finalizada'}],
                'vacina': [], 'medicamento': [], 'exame': [],
                'consulta_doenca': [{'id': 2, 'consulta_id': 1, 'doenca_id': 4,
                                    'veterinario_id': 3, 'veterinario_nome': 'Dra. Ana'}],
                'pet_doenca': [{'id': 5, 'consulta_doenca_id': 2, 'doenca_id': 4}],
                'doenca': [{'id': 4, 'nome': 'Dermatite'}]}
        result = execute('xano/function/clinical/history.xs', {'pet_id': 7}, rows)
        self.assertEqual(result['doencas'][0]['veterinario_nome'], 'Dra. Ana')
        self.assertEqual(result['diagnosticos'][0]['veterinario_nome'], 'Dra. Ana')

    def test_pdf_prints_name_and_textual_fallback(self):
        for name, expected in [('Dra. Ana', 'Dra. Ana'), (None, 'Nome não informado')]:
            with self.subTest(name=name):
                payload = export_payload()
                payload['consulta']['veterinario_nome'] = name
                document = map_consultation_document(payload, 7, 42)
                self.assertEqual(document.veterinarian_id, 3)
                rendered = render_consultation_pdf(document)
                content = '\n'.join(p.extract_text() for p in PdfReader(BytesIO(rendered)).pages)
                self.assertIn(expected, content)
                self.assertNotIn('ID 3', content)
