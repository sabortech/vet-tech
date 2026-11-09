"""Execute the production projection; database authorization is checked by smoke."""
import unittest
from test_clinical_projections import execute
from vet_tech.features.clinical.consultation_pdf import map_consultation_document


class PDFProjectionTests(unittest.TestCase):
    def test_scoped_projection_joins_names_and_keeps_diagnostics_distinct(self):
        fields={'id':42,'pet_id':7,'veterinario_id':3,'status':'finalizada','data_atendimento':'2026-11-04','motivo':'Consulta','diagnostico':'Texto','obs':'ç ã é'}
        rows={'consult':fields,'vacina':[],'medicamento':[],'exame':[],
              'consulta_doenca':[{'id':1,'pet_id':7,'consulta_id':42,'nome':'Dermatite','estado':'ativa'},
                                {'id':2,'pet_id':7,'consulta_id':42,'nome':'Alergia','estado':'controlada'},
                                {'id':3,'pet_id':7,'consulta_id':42}]}
        result=execute('xano/function/clinical/consultation_document.xs',{'pet_id':7,'pet_nome':'Amora','consulta_id':42},rows)
        self.assertEqual(result['pet'],{'id':7,'nome':'Amora'})
        self.assertEqual([r['nome'] for r in result['diagnosticos']],['Dermatite','Alergia','Não informado'])
        self.assertNotIn('doencas',result)
        result['auditoria_id']=91
        doc=map_consultation_document(result,7,42)
        self.assertIn('Dermatite',str(doc.sections));self.assertIn('Alergia',str(doc.sections))
