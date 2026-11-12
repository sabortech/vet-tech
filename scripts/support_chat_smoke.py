import sys,json,os
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
load_dotenv('.env')
sys.path.insert(0,str(Path.cwd()/'scripts'))
from clinical_smoke import Smoke,PRIVATE
import argparse
parser=argparse.ArgumentParser(description='Smoke real com fixtures sinteticas de desenvolvimento.')
parser.add_argument('--development',action='store_true',required=True)
parser.add_argument('--run',required=True)
args=parser.parse_args()
s=Smoke(PRIVATE/args.run)
s.setup()
checks=[]

def call(actor,action,**fields):
    if action=='close':fields.setdefault('expected_status','em_atendimento')
    profile='tutor' if actor.startswith('t') else 'veterinario'
    body={'payload':{'action':action,**fields}}
    if action=='create':body['bridge_key']=os.environ['SUPPORT_CHAT_BRIDGE_SECRET']
    code,data=s.api('POST',profile+'/chat',actor,body,'vettech-support')
    (s.folder/'last-support-response.json').write_text(json.dumps(data),encoding='utf-8')
    return code,data
def check(name,passed):
    checks.append({'name':name,'passed':bool(passed)})
    (s.folder/'support-results.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print(name,passed,flush=True)
    if not passed:raise SystemExit(1)

cid=str(uuid4())
creation=dict(conversation_id=cid,pet_id=s.data['pets']['a'],consent=True,reason='Dúvida sintética',context=[{'role':'user','content':'Pergunta sintética'},{'role':'assistant','content':'Encaminhamento sintético'}])
code,data=call('ta','create',**creation)
check('create',code==200 and data.get('ticket',{}).get('status')=='aguardando')
tid=data['ticket']['id']
s.data.setdefault('support_tickets',[]).append(tid);s.persist()
code,repeat=call('ta','create',**creation)
check('create_idempotent',code==200 and repeat['ticket']['id']==tid)
concurrent_creation=dict(creation,conversation_id=str(uuid4()))
with ThreadPoolExecutor(max_workers=2) as pool:
    concurrent=[pool.submit(call,'ta','create',**concurrent_creation) for _ in range(2)]
    concurrent=[f.result() for f in concurrent]
check('concurrent_create_idempotent',all(code==200 for code,_ in concurrent) and len({r['ticket']['id'] for _,r in concurrent})==1)
race_id=concurrent[0][1]['ticket']['id'];s.data['support_tickets'].append(race_id);s.persist()
with ThreadPoolExecutor(max_workers=2) as pool:
    race=[pool.submit(call,'ta','close',ticket_id=race_id,operation_id=str(uuid4()),reason='Cancelamento sintético',expected_status='aguardando'),pool.submit(call,'va','claim',ticket_id=race_id)]
    race=[f.result() for f in race]
check('cancel_claim_race',sum(code==200 for code,_ in race)==1)
wrong=dict(creation,conversation_id=str(uuid4()),pet_id=s.data['pets']['c'])
code,_=call('ta','create',**wrong);check('foreign_pet_rejected',code>=400)
code,_=call('ta','create',**dict(creation,conversation_id=str(uuid4()),consent=False))
check('missing_consent_rejected',code>=400)
code,_=s.api('POST','tutor/chat','ta',{'payload':{'action':'create',**creation}},'vettech-support')
check('direct_forged_context_rejected',code>=400)
code,_=call('tb','get',ticket_id=tid);check('other_tutor_denied',code>=400)
code,_=call('vb','get',ticket_id=tid);check('unassigned_vet_denied',code>=400)
code,queue=call('va','list')
row=next(r for r in queue.get('tickets',[]) if r['id']==tid)
check('minimal_queue',code==200 and set(row)<= {'id','created_at','updated_at','status','own','events'} and row['events']==[])
with ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(call,a,'claim',ticket_id=tid) for a in ('va','vb')]
    results=[f.result() for f in futures]
check('exclusive_claim',sum(code==200 for code,_ in results)==1)
vet=('va','vb')[next(i for i,(code,_) in enumerate(results) if code==200)]
other='vb' if vet=='va' else 'va'
code,_=call(other,'get',ticket_id=tid);check('losing_vet_denied',code>=400)
op=str(uuid4())
code,_=call('ta','send',ticket_id=tid,operation_id=op,message='Mensagem sintética')
check('send',code==200)
code,data=call('ta','send',ticket_id=tid,operation_id=op,message='Mensagem sintética')
check('send_idempotent',code==200 and len(data['ticket']['messages'])==1)
code,_=call('ta','send',ticket_id=tid,operation_id=op,message='Mudança de conteúdo')
check('operation_reuse_rejected',code>=400)
code,_=call(vet,'send',ticket_id=tid,operation_id=str(uuid4()),message='Orientação sintética')
check('vet_reply',code==200)
code,data=call(vet,'close',ticket_id=tid,operation_id=str(uuid4()),reason='Orientação sintética concluída')
check('close',code==200 and data['ticket']['status']=='encerrado')
code,_=call('ta','send',ticket_id=tid,operation_id=str(uuid4()),message='Mensagem tardia')
check('send_after_close_denied',code>=400)
code,data=call('ta','get',ticket_id=tid)
check('persistent_history',code==200 and len(data['ticket']['messages'])==2)
check('event_log_has_no_message_transcript',all(e.get('value')!='Mensagem sintética' for e in data['ticket']['events']))
code,_=call('ta','delete',ticket_id=tid);check('event_tampering_rejected',code>=400)
print('support_backend_smoke_complete',flush=True)
