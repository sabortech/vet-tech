"""Real non-clinical messaging checks, restricted to existing synthetic fixtures."""
import argparse,json,os,time,threading
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--development',action='store_true',required=True);ap.add_argument('--fixture-run',required=True);a=ap.parse_args()
 private=ROOT/'.venv/clinical-smoke';folder=(private/a.fixture_run).resolve();assert folder.is_relative_to(private.resolve())
 ledger=json.loads((folder/'ledger.json').read_text());assert not ledger.get('cleaned') and ledger['prefix'].startswith('qa-clinical-')
 load_dotenv(ROOT/'.env');origin=os.environ['XANO_API_BASE_URL'].rstrip('/');tokens={};checks=[]
 gate=threading.Lock();last=[0.0]
 with httpx.Client(timeout=50) as c:
  def post(group,path,data,token=''):
   for attempt in range(3):
    with gate:
     delay=3.0-(time.monotonic()-last[0])
     if delay>0:time.sleep(delay)
     last[0]=time.monotonic()
    r=c.post(f'{origin}/api:{group}/{path}',json=data,headers={'Authorization':'Bearer '+token} if token else {})
    if r.status_code!=429:return r
    time.sleep(21)
   return r
  def check(label,value):
   checks.append({'name':label,'passed':bool(value)});(folder/'direct-results.json').write_text(json.dumps(checks));print(label,bool(value),flush=True)
   if not value:raise RuntimeError(label)
  for key in ('ta','tb','va','vb'):
   account=ledger['actors'][key];assert account['email'].startswith(ledger['prefix']) and account['email'].endswith('@example.invalid')
   r=post('H62nB-j2','acesso/login',{'email':account['email'],'password':account['password']});check('login_'+key,r.status_code==200)
   data=r.json();assert data['identidade_id']==account['id'];tokens[key]=data['authToken']
  def call(actor,action,**kw):
   profile='tutor' if actor.startswith('t') else 'veterinario';r=post('vettech-support',profile+'/conversas',{'payload':{'action':action,**kw}},tokens[actor])
   if r.status_code>=400:(folder/'direct-last-error.json').write_text(r.text)
   return r
  search=call('va','tutors',search=str(ledger['actors']['ta']['id']));check('minimal_directory',search.status_code==200 and any(r['id']==ledger['actors']['ta']['id'] for r in search.json()['tutors']) and all(set(r)<= {'id','name'} for r in search.json()['tutors']))
  check('tutor_directory_denied',call('ta','tutors').status_code>=400)
  check('missing_veterinarian_denied',call('ta','start',tutor_id=ledger['actors']['tb']['id']).status_code>=400)
  vets=call('ta','veterinarians',search=str(ledger['actors']['va']['id']));check('tutor_veterinarian_directory',vets.status_code==200 and any(v['id']==ledger['actors']['va']['id'] for v in vets.json()['veterinarians']))
  started=call('ta','start',veterinario_id=ledger['actors']['va']['id']);check('tutor_starts_conversation',started.status_code==200)
  with ThreadPoolExecutor(max_workers=2) as pool:
   results=list(pool.map(lambda _:call('va','start',tutor_id=ledger['actors']['ta']['id']),range(2)))
  check('unique_pair_concurrent_start',all(r.status_code==200 for r in results) and len({r.json()['thread']['id'] for r in results})==1)
  tid=results[0].json()['thread']['id'];check('same_pair_both_directions',started.json()['thread']['id']==tid);op=str(uuid4());text='Verificação sintética de conversa privada'
  sent=call('va','send',thread_id=tid,operation_id=op,message=text);check('send',sent.status_code==200)
  repeat=call('va','send',thread_id=tid,operation_id=op,message=text);check('send_idempotent',repeat.status_code==200 and sum(m['id']==op for m in repeat.json()['thread']['messages'])==1)
  for actor in ('tb','vb'):
   check(actor+'_read_denied',call(actor,'get',thread_id=tid).status_code>=400)
   check(actor+'_write_denied',call(actor,'send',thread_id=tid,operation_id=str(uuid4()),message='indevida').status_code>=400)
   listed=call(actor,'list');check(actor+'_list_isolated',listed.status_code==200 and all(t['id']!=tid for t in listed.json()['threads']))
  read=call('ta','get',thread_id=tid,read_through=op,read_revision=0);check('read_receipt',read.status_code==200 and any(m['id']==op and m.get('read_at') for m in read.json()['thread']['messages']))
  reply=call('ta','send',thread_id=tid,operation_id=str(uuid4()),message='Resposta sintética');check('tutor_reply',reply.status_code==200)
  edited=call('va','edit',thread_id=tid,operation_id=str(uuid4()),message_id=op,expected_revision=0,message='Verificação sintética editada');check('edit',edited.status_code==200)
  deleted=call('va','delete',thread_id=tid,operation_id=str(uuid4()),message_id=op,expected_revision=1);check('delete_private_audit',deleted.status_code==200 and all(m['text']=='' for m in deleted.json()['thread']['messages'] if m['id']==op) and 'events' not in deleted.json()['thread'])
  check('persistent_pair',call('va','start',tutor_id=ledger['actors']['ta']['id']).json()['thread']['id']==tid)
 print('direct_chat_backend_verified',flush=True)
if __name__=='__main__':main()
