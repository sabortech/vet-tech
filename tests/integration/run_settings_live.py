"""Testes reais de conta: somente fixtures sintéticas em desenvolvimento confirmado."""
import argparse,json,sys,time,secrets,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import httpx
from vet_tech.features.auth.validation import is_valid_cpf
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Verifica configurações em Xano development com fixtures sintéticas.')
parser.add_argument('--phase',choices=('prepare','verify'),default='verify')
parser.add_argument('--fixtures',type=Path,default=root/'.env.settings-fixtures.json')
parser.add_argument('--foundation-fixtures',type=Path,default=root/'.env.foundation-fixtures.json')
args=parser.parse_args()
config=json.loads(args.foundation_fixtures.read_text())
assert config['environment']=='development' and config['synthetic'] is True
origin=config['origin']
account_api='/api:H62nB-j2/'
client=httpx.Client(base_url=origin,timeout=30)
def call(method,path,body=None,token=None,expected=(200,)):
 time.sleep(3)
 r=client.request(method,account_api+path,json=body,headers={'Authorization':'Bearer '+token} if token else {})
 if r.status_code not in expected:
  print(json.dumps({'method':method,'path':path,'status':r.status_code},ensure_ascii=False));raise RuntimeError('Contrato não atendido')
 return r.json() if r.is_success and r.content else None

def cpf():
 while True:
  base=str(secrets.randbelow(900000000)+100000000)
  for n in (10,11):
   value=sum(int(v)*(n-i) for i,v in enumerate(base))%11
   base+=str(0 if value<2 else 11-value)
  if is_valid_cpf(base):return base

def record(label):print(json.dumps({'scenario':label,'status':'passed'},ensure_ascii=False),flush=True)

mode=args.phase
fixture=args.fixtures
if mode=='prepare':
 actors=[]
 for tag in ('a','b'):
  data={'nome':'Fixture Configurações '+tag,'email':'settings-'+uuid.uuid4().hex+'@example.invalid','cpf':cpf(),'telefone':'11999999999','endereco':'Rua de teste','password':secrets.token_urlsafe(18)}
  call('POST','tutor/signup',data)
  login=call('POST','tutor/login',{'email':data['email'],'password':data['password']})
  actors.append({'data':data,'token':login['authToken'],'id':login.get('tutor_id')})
 fixture.write_text(json.dumps({'environment':'development','synthetic':True,'origin':origin,'actors':actors,'new_password':secrets.token_urlsafe(18)}))
 fixture.chmod(0o600)
 record('duas contas sintéticas criadas, credenciais em arquivo ignorado')
else:
 c=json.loads(fixture.read_text());assert c['environment']=='development' and c['synthetic'] is True and c['origin']==origin
 a,b=c['actors'];token=a['token'];c['new_password']=secrets.token_urlsafe(18)
 before_a=call('GET','tutor/account',token=token)
 before_b=call('GET','tutor/account',token=b['token'])
 assert before_a['email']==a['data']['email'] and 'cpf' not in before_a and 'password' not in before_a and '***' in before_a['cpf_mascarado']
 call('GET','tutor/account',expected=(401,403))
 call('GET','tutor/account',token='invalid-token',expected=(401,403))
 vet_login=call('POST','acesso/login',config['identity_credentials']['vet_a'])
 vet=vet_login['authToken']
 call('GET','tutor/account',token=vet,expected=(401,403))
 user=call('POST','auth/signup',{'name':'Fixture Settings User','email':'settings-user-'+uuid.uuid4().hex+'@example.invalid','password':secrets.token_urlsafe(18)})
 call('GET','tutor/account',token=user['authToken'],expected=(401,403))
 record('consulta própria, CPF mascarado e negativa sem token/token inválido/veterinário/user')
 changed={**a['data'],'nome':'Fixture atualizado','id':b['id'],'tutor_id':b['id'],'email':b['data']['email'],'cpf':b['data']['cpf'],'password':'forged-not-saved'}
 updated=call('PATCH','tutor/account',changed,token)
 assert updated['nome']=='Fixture atualizado' and updated['email']==before_a['email'] and updated['cpf_mascarado']==before_a['cpf_mascarado']
 assert call('GET','tutor/account',token=b['token'])==before_b
 call('PATCH','tutor/account',{'nome':'','telefone':'123','endereco':'x'},token,expected=(400,422))
 assert call('GET','tutor/account',token=token)==updated
 record('edição com allowlist, preservação da outra conta, CPF/e-mail/senha protegidos e sem escrita parcial')
 call('POST','tutor/password',{'current_password':'wrong','new_password':'xx','password_confirmation':'xx'},token,expected=(400,422))
 call('POST','tutor/password',{'current_password':a['data']['password'],'new_password':'xx','password_confirmation':'yy'},token,expected=(400,422))
 old_password=a['data']['password']
 call('POST','tutor/password',{'current_password':old_password,'new_password':c['new_password'],'password_confirmation':c['new_password']},token)
 a['data']['password']=c['new_password'];fixture.write_text(json.dumps(c))
 call('POST','tutor/login',{'email':a['data']['email'],'password':old_password},expected=(401,403))
 login=call('POST','tutor/login',{'email':a['data']['email'],'password':c['new_password']})
 a['data']['password']=c['new_password'];a['token']=login['authToken'];fixture.write_text(json.dumps(c))
 record('senha atual e confirmação verificadas, senha anterior rejeitada e nova aceita')
client.close()
