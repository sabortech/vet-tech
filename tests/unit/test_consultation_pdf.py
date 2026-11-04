import unittest
from copy import deepcopy
from vet_tech.features.clinical.consultation_pdf import (
    map_consultation_document, ConsultationPDFError, positive_id,
)


def export_payload(consultation_id=42, pet_id=7):
    return {
        'auditoria_id': 91,
        'pet': {'id': pet_id, 'nome': 'Amora — cão'},
        'consulta': {'id': consultation_id, 'pet_id': pet_id, 'veterinario_id': 3,
                     'status': 'finalizada', 'data_atendimento': '2026-11-04',
                     'agendada_para': '2026-11-04T14:00:00Z', 'motivo': 'Avaliação',
                     'diagnostico': 'Diagnóstico sintético', 'obs': 'Atenção à hidratação.\nç ã é'},
        'vacinas': [], 'medicamentos': [], 'diagnosticos': [], 'exames': [],
    }


class ConsultationDocumentTests(unittest.TestCase):
    def test_identity_dates_unicode_and_no_fabricated_fields(self):
        doc = map_consultation_document(export_payload(), '7', '42')
        self.assertEqual(doc.filename, 'vettech-consulta-42.pdf')
        self.assertEqual(dict(doc.fields)['Data do atendimento'], '04/11/2026')
        self.assertIn('11:00', dict(doc.fields)['Agendada para'])
        self.assertNotIn('CRMV', str(doc))
        self.assertEqual(doc.sections, ())

    def test_only_matching_complements_and_no_consolidated_condition(self):
        payload = export_payload()
        payload['medicamentos'] = [
            {'id': 1, 'pet_id': 7, 'consulta_id': 42, 'nome': 'Correto', 'dose': 0, 'unidade': 'mg'},
            {'id': 2, 'pet_id': 8, 'consulta_id': 42, 'nome': 'Pet alheio'},
            {'id': 3, 'pet_id': 7, 'consulta_id': 43, 'nome': 'Outra consulta'},
            {'id': 4, 'pet_id': 7, 'consulta_id': None, 'nome': 'Legado'},
        ]
        payload['doencas'] = [{'nome': 'Condição consolidada'}]
        doc = map_consultation_document(payload, 7, 42)
        self.assertEqual(len(doc.sections[0][1]), 1)
        self.assertIn(('Dose', '0'), doc.sections[0][1][0])
        self.assertNotIn('Consolidada', str(doc))
        for secret in ['Pet alheio', 'Outra consulta', 'Legado', 'Condição consolidada']:
            self.assertNotIn(secret, str(doc))

    def test_missing_optional_and_malformed_envelopes(self):
        payload = export_payload();payload['consulta']['obs'] = None
        self.assertEqual(dict(map_consultation_document(payload, 7, 42).fields)['Observações'], 'Não informado')
        for key in ['auditoria_id', 'pet', 'consulta', 'vacinas']:
            bad = deepcopy(payload);del bad[key]
            with self.subTest(key=key), self.assertRaises(ConsultationPDFError):
                map_consultation_document(bad, 7, 42)

    def test_unpublished_wrong_ids_and_boolean_ids_are_rejected(self):
        for status in ['agendada','em_atendimento','cancelada',None,'legado']:
            payload = export_payload();payload['consulta']['status'] = status
            with self.subTest(status=status), self.assertRaises(ConsultationPDFError):
                map_consultation_document(payload, 7, 42)
        for value in [True, False, -1, 0, '1/../../', '１', '1.0', 1.5, None]:
            with self.subTest(value=value), self.assertRaises(ConsultationPDFError):positive_id(value)
        with self.assertRaises(ConsultationPDFError):map_consultation_document(export_payload(), 8, 42)
        with self.assertRaises(ConsultationPDFError):map_consultation_document(export_payload(), 7, 43)

    def test_input_is_not_mutated_and_oversize_is_rejected(self):
        payload = export_payload();before=deepcopy(payload)
        map_consultation_document(payload, 7, 42)
        self.assertEqual(before,payload)
        payload['consulta']['obs'] = 'a' * 200_001
        with self.assertRaises(ConsultationPDFError):map_consultation_document(payload,7,42)


class PDFLayoutTests(unittest.TestCase):
    def test_dynamic_pdf_cover_pages_unicode_markup_and_optional_sections(self):
        from io import BytesIO
        from pypdf import PdfReader
        from unittest.mock import patch
        from vet_tech.features.clinical.consultation_pdf_template import render_consultation_pdf
        payload=export_payload()
        payload['consulta']['obs']='<img src="http://example.invalid/secret"/>\nç ã é fim'
        with patch('urllib.request.urlopen',side_effect=AssertionError('No network')):
            data=render_consultation_pdf(map_consultation_document(payload,7,42))
        reader=PdfReader(BytesIO(data));text='\n'.join(page.extract_text() for page in reader.pages)
        self.assertTrue(data.startswith(b'%PDF-'));self.assertEqual(len(reader.pages),2)
        self.assertIn('Amora — cão',text);self.assertIn('ç ã é fim',text)
        self.assertIn('<img src="http://example.invalid/secret"/>',text)
        self.assertNotIn('LUNA',text);self.assertNotIn('000184',text)
        self.assertNotIn('fictício',text);self.assertNotIn('Vacinas',text)
        self.assertLess(len(data),2*1024*1024)
        for page in reader.pages:self.assertAlmostEqual(float(page.mediabox.width),595.2756,places=2)

    def test_very_long_paragraph_and_table_row_are_not_truncated(self):
        from io import BytesIO
        from pypdf import PdfReader
        from vet_tech.features.clinical.consultation_pdf_template import render_consultation_pdf
        payload=export_payload();payload['consulta']['obs']=('Observação com acentuação.\n'*800)+'ULTIMA_OBSERVACAO'
        payload['exames']=[{'id':3,'pet_id':7,'consulta_id':42,'tipo':'Exame sintético',
                           'resultado':('Resultado extenso. '*1500)+'ULTIMO_RESULTADO'}]
        data=render_consultation_pdf(map_consultation_document(payload,7,42))
        reader=PdfReader(BytesIO(data));text=''.join(p.extract_text() for p in reader.pages)
        self.assertGreater(len(reader.pages),5)
        self.assertIn('ULTIMA_OBSERVACAO',text);self.assertIn('ULTIMO_RESULTADO',text)
        self.assertIn('Página 2',text)

    def test_busy_render_slots_fail_closed(self):
        from vet_tech.features.clinical.consultation_pdf_template import _SLOTS,render_consultation_pdf
        _SLOTS.acquire();_SLOTS.acquire()
        try:
            with self.assertRaises(ConsultationPDFError):render_consultation_pdf(map_consultation_document(export_payload(),7,42))
        finally:_SLOTS.release();_SLOTS.release()

    def test_output_size_limit_fails_without_partial_pdf(self):
        from unittest.mock import patch
        from vet_tech.features.clinical.consultation_pdf_template import render_consultation_pdf
        with patch('vet_tech.features.clinical.consultation_pdf_template.MAX_PDF_BYTES',10):
            with self.assertRaises(ConsultationPDFError):render_consultation_pdf(map_consultation_document(export_payload(),7,42))
