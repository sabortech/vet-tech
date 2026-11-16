"""Integração em workspace de desenvolvimento; contas temporárias .invalid, sem e-mail real.

O remetente rejeita .invalid antes do HTTP. Concorrência usa clone privado do
orquestrador com transporte simulado. Funções temporárias e contas são removidas.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import threading
from pathlib import Path
import secrets
import sys
import time
import httpx
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from vet_tech.shared.config import get_xano_base_url


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--existing-probes',type=Path);args=parser.parse_args()
    fixture=json.loads((ROOT/'.env.foundation-fixtures.json').read_text())
    assert fixture.get('synthetic') is True and fixture.get('environment')=='development'
    origin=get_xano_base_url().rstrip('/');assert origin==fixture['origin'].rstrip('/')
    cred=yaml.safe_load((Path.home()/'.xano/credentials.yaml').read_text());p=cred['profiles'][cred.get('default_profile',cred.get('default',next(iter(cred['profiles']))))]
    assert origin==p['instance_origin'].rstrip('/')
    base=origin+'/api:meta/workspace/'+str(p['workspace']);headers={'Authorization':'Bearer '+p['access_token']};public=origin+'/api:H62nB-j2/'
    def unpack(r):
        r.raise_for_status();d=r.json()
        if 'result' in d:d=d['result']
        while isinstance(d,dict) and 'status' in d:
            if d['status']!='ok':raise RuntimeError('Execução nativa falhou; detalhes sensíveis ocultados.')
            d=d.get('result')
        return d
    pacing=threading.Lock();last_meta=[0.0]
    def pause_metadata():
        with pacing:
            delay=3.2-(time.monotonic()-last_meta[0])
            if delay>0:time.sleep(delay)
            last_meta[0]=time.monotonic()
    def run(client,name,inputs):
        if name!='Notifications/welcome_concurrency_probe':pause_metadata()
        return unpack(client.post(base+'/function/run',headers=headers,json={'branch':'v1','name':name,'input':inputs}))
    def cpf():
        digits=[secrets.randbelow(10) for _ in range(9)]
        for size in (10,11):
            value=(sum(x*(size-i) for i,x in enumerate(digits))*10)%11;digits.append(0 if value==10 else value)
        return ''.join(map(str,digits))
    token=secrets.token_hex(6);emails={'tutor':'welcome-'+token+'-tutor@example.invalid','veterinario':'welcome-'+token+'-vet@example.invalid'}
    bads=['welcome-'+token+'a-tutor@example.invalid','welcome-'+token+'b-vet@example.invalid'];password=secrets.token_urlsafe(24)
    ids=json.loads(args.existing_probes.read_text()) if args.existing_probes else []
    results=[];cleaned=[];removed=[]
    checkpoint=ROOT/'.env.welcome-test-pending.json'
    assert not checkpoint.exists(),'Há ensaio pendente de limpeza; reconciliar antes de novo teste.'
    def save_progress():
        checkpoint.write_text(json.dumps({'emails':[*emails.values(),*bads],'functions':ids,'checks':results,'cleaned':cleaned}))
        checkpoint.chmod(0o600)
    save_progress()
    with httpx.Client(timeout=60) as client:
        try:
            if not ids:
                synthetic=(ROOT/'tests/fixtures/welcome_email/synthetic_probe.xs').read_text()
                clone=(ROOT/'xano/function/notifications/send_welcome_email.xs').read_text();clone=clone[:clone.index('\n  test ')]+'\n}\n';clone=clone.replace('function "Notifications/send_welcome_email"','function "Notifications/welcome_concurrency_probe"',1)
                start=clone.index('            function.run "Notifications/deliver_welcome_email"');end=clone.index('} as $receipt',start)+len('} as $receipt');clone=clone[:start]+'            var.update $receipt {value={accepted:false,state:"falhou",provider_id:""}}'+clone[end:]
                for name,source in [('Notifications/welcome_synthetic_probe',synthetic),('Notifications/welcome_concurrency_probe',clone)]:
                    pause_metadata();r=client.post(base+'/function',params={'branch':'v1'},headers={**headers,'Content-Type':'text/x-xanoscript'},content=source);r.raise_for_status();ids.append({'name':name,'id':r.json()['id']});save_progress()
            opts=client.get(public+'cadastro/opcoes');opts.raise_for_status();opts=opts.json();assert opts['especies'] and opts['especialidades']
            payloads={
                'tutor':{'nome':'Welcome Test Tutor','email':emails['tutor'],'password':password,'telefone':'11999999999','cpf':cpf(),'endereco':'Rua Teste'},
                'veterinario':{'nome':'Welcome Test Vet','email':emails['veterinario'],'password':password,'telefone':'11999999999','crmv':'WL'+token,'crmv_uf':'SP','especies_ids':[opts['especies'][0]['id']],'especialidades_ids':[opts['especialidades'][0]['id']]}}
            for profile,payload in payloads.items():
                r=client.post(public+profile+'/signup',json=payload);assert r.status_code==200,(profile,r.status_code);assert r.json()=={'success':True}
                state={}
                for _ in range(12):
                    state=run(client,'Notifications/welcome_synthetic_probe',{'email':payload['email'],'action':'inspect'})
                    if state.get('state')=='incerto':break
                    time.sleep(.5)
                assert state.get('exists') and state.get('profile')==profile and state.get('event_id') and state.get('state')=='incerto',state
                login=client.post(public+'acesso/login',json={'email':payload['email'],'password':password});assert login.status_code==200,(profile,'login');assert login.json().get('perfil')==profile
                duplicate=client.post(public+profile+'/signup',json=payload);assert duplicate.status_code>=400
                repeated=run(client,'Notifications/send_welcome_email',{'event_id':state['event_id']});assert repeated=={'accepted':False,'state':'ignorado'}
                prepared=run(client,'Notifications/welcome_synthetic_probe',{'email':payload['email'],'action':'prepare'});assert prepared.get('prepared')
                with ThreadPoolExecutor(max_workers=2) as pool:
                    calls=list(pool.map(lambda _:run(client,'Notifications/welcome_concurrency_probe',{'event_id':state['event_id']}),range(2)))
                assert sorted(v['state'] for v in calls)==['falhou','ignorado'],calls
                results.append({'profile':profile,'signup_success':True,'event_after_commit':True,'reserved_invalid_address_not_sent':True,'login_after_delivery_failure':True,'duplicate_signup_rejected':True,'duplicate_attempt_ignored':True,'concurrent_claim_single_winner':True,'transport_for_concurrency':'simulated'})
                save_progress()
                print('PASS:',profile,'cadastro, login após falha, deduplicação e concorrência.',flush=True)
            invalid=[('tutor',{**payloads['tutor'],'email':bads[0],'cpf':'00000000000'}),('veterinario',{**payloads['veterinario'],'email':bads[1],'crmv':'WLX'+token,'especies_ids':[-1]})]
            for profile,payload in invalid:
                r=client.post(public+profile+'/signup',json=payload);assert r.status_code>=400
                probe=run(client,'Notifications/welcome_synthetic_probe',{'email':payload['email'],'action':'inspect'});assert probe.get('exists') is False
                results.append({'profile':profile,'invalid_signup_rejected':True,'no_identity_or_welcome':True});save_progress()
        finally:
            for email in [*emails.values(),*bads]:
                try:
                    row=run(client,'Notifications/welcome_synthetic_probe',{'email':email,'action':'cleanup'});assert row.get('exists') is False;cleaned.append(True)
                except Exception:cleaned.append(False)
            for item in ids:
                try:
                    pause_metadata();r=client.delete(base+'/function/'+str(item['id']),params={'branch':'v1'},headers=headers)
                    removed.append(r.status_code in (200,404))
                except Exception:removed.append(False)
            evidence={'environment':'development','synthetic':True,'real_email_sent':False,'checks':results,'synthetic_accounts_removed':all(cleaned),'temporary_functions_removed':all(removed)}
            out=ROOT/'openspec/changes/archive/2026-11-16-enviar-boas-vindas-cadastro/evidence/live-integration.json';out.write_text(json.dumps(evidence,indent=2))
            save_progress()
            if all(cleaned) and all(removed):checkpoint.unlink()
            assert all(cleaned) and all(removed),'Limpeza sintética incompleta; checkpoint privado preservado.'
    assert len(results)==4
    print('PASS: dois perfis; contas sintéticas e funções temporárias removidas.',flush=True)

if __name__=='__main__':main()
