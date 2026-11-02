"""Synthetic contract, clinical projection and stale-selection verification."""
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from test_clinical_state import session, consume, TARGET
from test_clinical_projections import execute
from vet_tech.features.auth.state import State
from vet_tech.features.clinical.state import consultation_summary
from vet_tech.shared.xano_client import XanoRequestError


class ConsultationsTests(unittest.IsolatedAsyncioTestCase):
    def test_allergy_names_states_and_dates_without_invented_unit(self):
        data = consultation_summary({'nome':'Max','peso_atual':0}, {
            'doencas':[{'nome':'Alergia alimentar','estado':'controlada'}, {'nome':'Dermatite'}, {'nome':'Dermatite alérgica'}, {'nome':'Dermatite não alérgica'}],
            'diagnosticos':[{'nome':'Alergia a penicilina','estado':'ativa'}],
            'vacinas':[{'vacina':'Antiga','data_aplicacao':'2020-01-01'}, {'vacina':'Recente','data_aplicacao':'2026-01-01'}],
            'consultas':[{'data_atendimento':'2020-01-01'}, {'data_atendimento':'2026-02-01'}]})
        self.assertEqual(data['peso'], '0')
        self.assertIn('Alergia alimentar · controlada',data['alergias'])
        self.assertIn('penicilina',data['alergias'])
        self.assertIn('Dermatite alérgica',data['alergias'])
        self.assertNotIn('não alérgica',data['alergias'])
        self.assertIn('Recente',data['ultima_vacina'])
        self.assertEqual(data['ultima_consulta'],'01/02/2026')
        self.assertEqual(consultation_summary({}, {})['alergias'],'Alergias não informadas')

    def test_filters_precede_pagination_and_private_pet_search_is_excluded(self):
        rows={'reservations':[{'id':i,'pet_id':5,'status':'finalizada' if i<30 else 'agendada', 'agendada_para':1893544200000} for i in range(1,56)],
              'consents':[{'pet_id':5}], 'pets':[{'id':5,'nome':'Max'}]}
        result=execute('xano/api/clinical/agenda_GET.xs', {'aba':'Concluídas','busca':'max','page':2}, rows)
        self.assertEqual(result['total'],29)
        self.assertEqual([r['id'] for r in result['items']],[26,27,28,29])
        rows['consents']=[]
        result=execute('xano/api/clinical/agenda_GET.xs', {'aba':'Concluídas','busca':'max'}, rows)
        self.assertEqual(result['total'],0)
        result=execute('xano/api/clinical/agenda_GET.xs', {'aba':'inválida'}, rows)
        self.assertIn('error',result)

    async def test_old_backend_does_not_claim_filtered_results(self):
        state=session('veterinario'); state.vet_section='Consultas'
        with patch(TARGET,new_callable=AsyncMock, return_value={'items':[], 'total':50}):
            await consume(State.filter_consultations.fn(state,'tab','Concluídas'))
        self.assertEqual(state.upcoming_rows,[])
        self.assertEqual(state.agenda_total,0)
        self.assertIn('Xano',state.clinic_message)

    async def test_selection_stale_response_and_revocation(self):
        state=session('veterinario'); state.vet_section='Consultas'
        state.upcoming_rows=[{'id':'1','pet_id':'5','autorizado':'sim','status':'agendada'}, {'id':'2','pet_id':'6','autorizado':'sim','status':'em_atendimento'}]
        first=asyncio.Event(); release=asyncio.Event()
        async def request(*args,**kwargs):
            if '/5/' in args[2]:
                first.set(); await release.wait()
                return {'pet':{'nome':'Max'},'historico':{}}
            return {'pet':{'nome':'Mel'},'historico':{}}
        with patch(TARGET,side_effect=request):
            task=asyncio.create_task(consume(State.select_consultation.fn(state,'1')))
            await first.wait()
            await consume(State.select_consultation.fn(state,'2'))
            release.set(); await task
        self.assertEqual(state.consultation_info['nome'],'Mel')
        self.assertEqual(state.consultation_info['status'],'em_atendimento')
        with patch(TARGET,new_callable=AsyncMock,side_effect=XanoRequestError('Revogado',status_code=403)):
            await consume(State.select_consultation.fn(state,'1'))
        self.assertEqual(state.consultation_info,{})
        self.assertFalse(state.consultation_summary_loading)
        self.assertEqual(state.consultation_selected,'')

    async def test_logout_discards_in_flight_summary(self):
        state=session('veterinario'); state.vet_section='Consultas'
        state.upcoming_rows=[{'id':'1','pet_id':'5','autorizado':'sim'}]
        started=asyncio.Event(); release=asyncio.Event()
        async def request(*args,**kwargs):
            started.set(); await release.wait()
            return {'pet':{'nome':'Max'},'historico':{}}
        with patch(TARGET,side_effect=request):
            task=asyncio.create_task(consume(State.select_consultation.fn(state,'1')))
            await started.wait(); state._clear_clinical_session(); release.set(); await task
        self.assertEqual(state.consultation_info,{})
        self.assertFalse(state.consultation_summary_loading)

    def test_cancelled_tab_excludes_active_and_completed_records(self):
        rows={'reservations':[{'id':i,'pet_id':5,'status':status,'agendada_para':1893544200000}
            for i,status in enumerate(('agendada','cancelada','em_atendimento','finalizada'),1)],
            'consents':[{'pet_id':5}], 'pets':[{'id':5,'nome':'Max'}]}
        result=execute('xano/api/clinical/agenda_GET.xs',{'aba':'Canceladas','page':1},rows)
        self.assertEqual([r['id'] for r in result['items']],[2])
        self.assertEqual(result['contrato_consultas'],2)
        result=execute('xano/api/clinical/agenda_GET.xs',{'aba':'Pendentes','page':1},rows)
        self.assertEqual([r['id'] for r in result['items']],[1,3])

    async def test_cancelled_tab_requires_new_contract_and_resets_page(self):
        state=session('veterinario');state.vet_section='Consultas';state.agenda_page=3
        with patch(TARGET,new_callable=AsyncMock,return_value={'items':[],'total':0,'contrato_consultas':1}):
            await consume(State.filter_consultations.fn(state,'tab','Canceladas'))
        self.assertEqual(state.agenda_page,1)
        self.assertIn('Xano',state.clinic_message)
        with patch(TARGET,new_callable=AsyncMock,return_value={'items':[{'id':9,'pet_id':5,'status':'cancelada','agendada_para':1893544200000}],'total':1,'contrato_consultas':2}):
            await consume(State.load_agenda.fn(state))
        self.assertEqual(state.upcoming_rows[0]['status_label'],'Cancelada')
        self.assertEqual(state.clinic_message,'')
