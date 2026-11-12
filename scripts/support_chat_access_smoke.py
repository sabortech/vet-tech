import sys,json,os,time
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv('.env')
sys.path.insert(0,str(Path.cwd()/'scripts'))
from clinical_smoke import Smoke,PRIVATE
import argparse
parser=argparse.ArgumentParser(description='Verifica independencia entre chat e consentimento clinico com fixtures sinteticas.')
parser.add_argument('--run',required=True)
parser.add_argument('--development',action='store_true',required=True)
args=parser.parse_args()
s=Smoke(PRIVATE/args.run)
def check(name,passed):
    print(name,passed,flush=True)
    if not passed:raise SystemExit(1)
def chat(actor,action,**fields):
    role='tutor' if actor[0]=='t' else 'veterinario'
    body={'payload':{'action':action,**fields}}
    if action=='close':body['payload']['expected_status']='em_atendimento'
    if action=='create':body['bridge_key']=os.environ['SUPPORT_CHAT_BRIDGE_SECRET']
    code,data=s.api('POST',role+'/chat',actor,body,'vettech-support')
    (s.folder/'access-chat-response.json').write_text(json.dumps(data),encoding='utf-8')
    return code,data
pet=s.data['pets']['b'];vet=s.data['actors']['va']['id']
code,data=chat('ta','create',conversation_id=str(uuid4()),pet_id=pet,consent=True,reason='Teste consentimento independente',context=[{'role':'user','content':'Teste sintético'}])
check('access_fixture_ticket',code==200)
tid=data['ticket']['id'];s.data.setdefault('support_tickets',[]).append(tid);s.persist()
code,_=chat('va','claim',ticket_id=tid);check('claim_without_clinical_consent',code==200)
code,_=s.api('GET',f'veterinario/pets/{pet}/historico','va');check('record_denied_without_consent',code>=400)
existing=next((r for r in s.store.pages(s.store.url('acesso_autorizado')) if r.get('pet_id')==pet and r.get('veterinario_id')==vet),None)
if existing:
    consent=existing
    code,_=s.api('PUT',f'tutor/pets/{pet}/acessos/{consent["id"]}','ta',{'status':'ativo'})
else:
    consent,code=s.store.write('POST','acesso_autorizado',{'pet_id':pet,'veterinario_id':vet,'status':'ativo','concedido_em':int(time.time()*1000)})
check('synthetic_consent_created',code in (200,201))
s.track('acesso_autorizado',consent);s.persist()
code,_=s.api('GET',f'veterinario/pets/{pet}/historico','va');check('authorized_record_read',code==200)
code,_=s.api('PUT',f'tutor/pets/{pet}/acessos/{consent["id"]}','ta',{'status':'revogado'});check('tutor_revokes_consent',code==200)
code,_=s.api('GET',f'veterinario/pets/{pet}/historico','va');check('record_denied_after_revocation',code>=400)
code,_=chat('va','send',ticket_id=tid,operation_id=str(uuid4()),message='Mensagem após revogação clínica')
check('chat_continues_after_revocation',code==200)
logs=s.store.pages(s.store.url('log_acesso'))
check('clinical_read_audited',any(r.get('pet_id')==pet and r.get('veterinario_id')==vet and r.get('acao')=='visualizar_historico' for r in logs))
code,_=chat('ta','close',ticket_id=tid,operation_id=str(uuid4()),reason='Teste concluído');check('access_fixture_closed',code==200)
