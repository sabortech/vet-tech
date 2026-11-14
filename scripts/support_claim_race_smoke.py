"""Real claim race using existing synthetic development actors; no real tickets."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import threading
import time
from uuid import uuid4
import httpx
import yaml
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.venv/clinical-smoke'


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--development',action='store_true',required=True);parser.add_argument('--fixture-run',required=True);args=parser.parse_args()
 folder=(PRIVATE/args.fixture_run).resolve();assert folder.is_relative_to(PRIVATE.resolve())
 path=folder/'ledger.json';ledger=json.loads(path.read_text());assert not ledger.get('cleaned') and ledger['prefix'].startswith('qa-clinical-')
 load_dotenv(ROOT/'.env');cfg=yaml.safe_load((Path.home()/'.xano/credentials.yaml').read_text());profile=cfg['profiles'].get('vetech') or cfg['profiles'][cfg['default']]
 assert int(profile['workspace'])==167758
 origin=os.environ['XANO_API_BASE_URL'].rstrip('/');assert profile['instance_origin'].rstrip('/')==origin
 secret=os.environ['SUPPORT_CHAT_BRIDGE_SECRET'];assert secret
 checks=[];tokens={};ticket_id=None;operation_run=str(uuid4());record={'conversation_id':operation_run,'ticket_id':None,'checks':checks}
 evidence=folder/f'claim-race-{operation_run}.json';evidence.write_text(json.dumps(record))
 with httpx.Client(timeout=40) as client:
  def request(group,route,body,token=None):
   for attempt in range(3):
    r=client.post(f'{origin}/api:{group}/{route}',json=body,headers={'Authorization':'Bearer '+token} if token else {})
    if r.status_code!=429 or attempt==2:return r
    time.sleep(min(10,max(1,float(r.headers.get('Retry-After','5')))))
  def check(name,value):
   checks.append({'name':name,'passed':bool(value)});evidence.write_text(json.dumps(record));print(name,bool(value),flush=True)
   if not value:raise RuntimeError('Verificação falhou: '+name)
  for actor in ['ta','va','vb']:
   account=ledger['actors'][actor];assert account['email'].startswith(ledger['prefix']) and account['email'].endswith('@example.invalid')
   r=request('H62nB-j2','acesso/login',{'email':account['email'],'password':account['password']})
   check('synthetic_login_'+actor,r.status_code==200)
   body=r.json();check('synthetic_identity_'+actor,body['identidade_id']==account['id'] and body['perfil']==('tutor' if actor=='ta' else 'veterinario'))
   tokens[actor]=body['authToken']
  def call(actor,action,**fields):
   body={'payload':{'action':action,**fields}}
   if action=='create':body['bridge_key']=secret
   return request('vettech-support',('tutor' if actor=='ta' else 'veterinario')+'/chat',body,tokens[actor])
  try:
   created=call('ta','create',conversation_id=operation_run,pet_id=ledger['pets']['a'],consent=True,reason='Teste sintético de assunção exclusiva',context=[{'role':'user','content':'Verificação sintética da fila'},{'role':'assistant','content':'Encaminhamento de teste'}])
   check('synthetic_ticket_created',created.status_code==200)
   ticket_id=created.json()['ticket']['id'];record['ticket_id']=ticket_id;ledger.setdefault('support_tickets',[]).append(ticket_id);path.write_text(json.dumps(ledger));evidence.write_text(json.dumps(record))
   gate=threading.Barrier(2)
   def claim(actor):gate.wait();return call(actor,'claim',ticket_id=ticket_id)
   with ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(claim,actor) for actor in ['va','vb']];results=[f.result() for f in futures]
   successes=[i for i,r in enumerate(results) if r.status_code==200]
   check('exactly_one_veterinarian_claims',len(successes)==1 and all(r.status_code!=429 for r in results))
   winner=['va','vb'][successes[0]];loser='vb' if winner=='va' else 'va'
   check('loser_cannot_reclaim',call(loser,'claim',ticket_id=ticket_id).status_code>=400)
   check('loser_cannot_read',call(loser,'get',ticket_id=ticket_id).status_code>=400)
   queue=call(loser,'list');check('assigned_ticket_removed_from_other_queue',queue.status_code==200 and not any(t['id']==ticket_id for t in queue.json()['tickets']))
  finally:
   if ticket_id:
    closed=False
    for actor,status in [('va','em_atendimento'),('vb','em_atendimento'),('ta','aguardando')]:
     r=call(actor,'close',ticket_id=ticket_id,expected_status=status,operation_id=str(uuid4()),reason='Verificação sintética concluída')
     if r.status_code==200:closed=True;break
    record['synthetic_ticket_closed']=closed;evidence.write_text(json.dumps(record));print('synthetic_ticket_closed',closed,flush=True)
    if not closed:raise RuntimeError('Chamado sintético precisa de encerramento; veja ledger privado')
 print('claim_race_verified',flush=True)


if __name__=='__main__':main()
