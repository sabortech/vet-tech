"""Five civil days, filtering before pagination, and daily card grouping."""
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from test_clinical_projections import execute
from test_clinical_state import session, consume, TARGET
from vet_tech.features.auth.state import State
from vet_tech.features.clinical.state import consultation_days

PATH = 'xano/api/clinical/agenda_GET.xs'
def stamp(iso):
    return int(datetime.fromisoformat(iso.replace('Z','+00:00')).timestamp() * 1000)
NOW = stamp('2026-11-02T12:00:00-03:00')
def row(value, day, status='agendada', pet=5):
    return {'id':value,'pet_id':pet,'status':status,'agendada_para':stamp(day+'T09:00:00-03:00')}
def variables(rows):
    return {'reservations':rows, 'consents':[{'pet_id':5}], 'pets':[{'id':5,'nome':'Jessy','foto':None}]}

class ConsultationFilterTests(unittest.TestCase):
    def test_next_five_days_include_today_and_both_boundaries(self):
        rows=[row(i,'2026-11-'+str(i).zfill(2)) for i in range(1,8)]
        result=execute(PATH,{'aba':'Próximas'},variables(rows),NOW)
        self.assertEqual([r['id'] for r in result['items']],[2,3,4,5,6])
        self.assertEqual(result['contrato_consultas'],3)
        self.assertIsNone(result['items'][0]['pet_foto'])

    def test_tabs_keep_their_states_and_day_mode_is_unchanged(self):
        rows=[row(i,'2026-11-02',status) for i,status in enumerate(['agendada','em_atendimento','finalizada','cancelada','legado'],1)]
        for tab,expected in [('Pendentes',[1,2]),('Hoje',[1,2]),('Próximas',[1,2]),('Concluídas',[3]),('Canceladas',[4])]:
            with self.subTest(tab=tab):
                self.assertEqual([r['id'] for r in execute(PATH,{'aba':tab},variables(rows),NOW)['items']],expected)
        self.assertEqual(len(execute(PATH,{'dia':'2026-11-02'},variables(rows),NOW)['items']),5)

    def test_local_midnight_and_year_boundary(self):
        now=stamp('2026-12-31T01:00:00Z') # Still December 30 in Sao Paulo.
        rows=[row(i,day) for i,day in enumerate(['2026-12-29','2026-12-30','2026-12-31','2027-01-01','2027-01-02','2027-01-03','2027-01-04'])]
        rows+=[{'id':99,'pet_id':5,'status':'agendada','agendada_para':stamp('2026-12-31T02:59:59Z')},
               {'id':100,'pet_id':5,'status':'agendada','agendada_para':stamp('2026-12-31T03:00:00Z')}]
        result=execute(PATH,{'aba':'Próximas'},variables(rows),now)
        self.assertEqual({r['id'] for r in result['items']},{1,2,3,4,5,99,100})
        today=execute(PATH,{'aba':'Hoje'},variables(rows),now)
        self.assertEqual({r['id'] for r in today['items']},{1,99})

    def test_filters_precede_paging_and_search_never_uses_revoked_names(self):
        rows=[row(i,'2026-11-03') for i in range(1,31)]+[row(90,'2026-11-07')]
        result=execute(PATH,{'aba':'Próximas','busca':'jessy','estado':'agendada','page':2},variables(rows),NOW)
        self.assertEqual(result['total'],30)
        self.assertEqual([r['id'] for r in result['items']],[26,27,28,29,30])
        data=variables(rows);data['consents']=[]
        self.assertEqual(execute(PATH,{'aba':'Próximas','busca':'jessy'},data,NOW)['total'],0)
        redacted=execute(PATH,{'aba':'Próximas'},data,NOW)['items'][0]
        self.assertEqual(set(redacted),{'id','status','agendada_para','autorizado'})

    def test_grouping_sorts_cards_and_labels_relative_days(self):
        rows=[row(4,'2026-11-04'),row(3,'2026-11-03'),row(2,'2026-11-02'),row(1,'2026-11-02')]
        for r in rows: r['id']=str(r['id']);r['agendada_para']=str(r['agendada_para'])
        groups=consultation_days(rows,'2026-11-02')
        self.assertEqual([g['label'] for g in groups],['Hoje — 02/11/2026','Amanhã — 03/11/2026','04/11/2026'])
        self.assertEqual(sum(len(g['items']) for g in groups),4)
        self.assertEqual(consultation_days([],'2026-11-02'),[])
        self.assertEqual(consultation_days(rows[1:2],'2026-11-02')[0]['label'],'Amanhã — 03/11/2026')

    def test_grouping_uses_scheduled_local_date_not_clinical_date(self):
        groups=consultation_days([{'id':'1','agendada_para':str(stamp('2026-11-03T01:00:00Z')),'data_atendimento':'2026-10-01'}],'2026-11-02')
        self.assertEqual(groups[0]['date'],'2026-11-02')

class ConsultationContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_upcoming_requires_three_and_filter_resets_page(self):
        state=session('veterinario');state.vet_section='Consultas';state.agenda_page=4
        for version in (1,2):
            with patch(TARGET,AsyncMock(return_value={'items':[],'total':9,'contrato_consultas':version})):
                await consume(State.filter_consultations.fn(state,'tab','Próximas'))
            self.assertEqual(state.agenda_page,1)
            self.assertIn('Xano',state.clinic_message)
        with patch(TARGET,AsyncMock(return_value={'items':[row(1,'2026-11-02')],'total':1,'contrato_consultas':3})):
            await consume(State.load_agenda.fn(state))
        self.assertEqual(state.clinic_message,'')
        self.assertEqual(len(state.upcoming_rows),1)
        self.assertEqual(state.consultation_selected,'')
