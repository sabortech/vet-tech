"""Força falha após inserir identidade/evento em clones privados para provar rollback.

Usa somente .invalid, não publica endpoints e remove os diagnósticos ao final.
"""
import json
from pathlib import Path
import re
import secrets
import sys
import time
import httpx
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from vet_tech.shared.config import get_xano_base_url


def main():
    cfg=json.loads((ROOT/'.env.foundation-fixtures.json').read_text());assert cfg.get('synthetic') is True and cfg.get('environment')=='development'
    origin=get_xano_base_url().rstrip('/');assert origin==cfg['origin'].rstrip('/')
    c=yaml.safe_load((Path.home()/'.xano/credentials.yaml').read_text());p=c['profiles'][c.get('default_profile',c.get('default',next(iter(c['profiles']))))];assert origin==p['instance_origin'].rstrip('/')
    base=origin+'/api:meta/workspace/'+str(p['workspace']);headers={'Authorization':'Bearer '+p['access_token']};public=origin+'/api:H62nB-j2/';ids=[];results=[];cleaned=[];emails=[]
    def call(client,name,payload):
        time.sleep(3.2);r=client.post(base+'/function/run',headers=headers,json={'branch':'v1','name':name,'input':payload});r.raise_for_status();return r.json()['result']
    def unpack(d):
        if d.get('status')!='ok':raise RuntimeError('Diagnóstico recusado; detalhes ocultados.')
        return d['result']
    def cpf():
        digits=[secrets.randbelow(10) for _ in range(9)]
        for size in (10,11):
            x=(sum(v*(size-i) for i,v in enumerate(digits))*10)%11;digits.append(0 if x==10 else x)
        return ''.join(map(str,digits))
    token=secrets.token_hex(6)
    with httpx.Client(timeout=60) as client:
        try:
            helper=(ROOT/'tests/fixtures/welcome_email/synthetic_probe.xs').read_text();r=client.post(base+'/function',params={'branch':'v1'},headers={**headers,'Content-Type':'text/x-xanoscript'},content=helper);r.raise_for_status();ids.append(r.json()['id'])
            options=client.get(public+'cadastro/opcoes');options.raise_for_status();options=options.json()
            for profile,rel in [('tutor','auth/tutor_signup_POST.xs'),('veterinario','veterinario/signup_POST.xs')]:
                source=(ROOT/'xano/api/authentication'/rel).read_text();name='Notifications/welcome_rollback_'+profile
                source=re.sub(r'^query "[^"]+" verb=POST',lambda _: 'function "'+name+'"',source,count=1)
                source=re.sub(r'^  api_group = .*\n','',source,flags=re.M);source=re.sub(r'^  guid = .*\n','',source,flags=re.M)
                source=source.replace('} as $welcome_event','} as $welcome_event\n        precondition (false) {\n          error_type="inputerror"\n          error="Rollback de teste após evento."\n        }',1)
                time.sleep(3.2);r=client.post(base+'/function',params={'branch':'v1'},headers={**headers,'Content-Type':'text/x-xanoscript'},content=source);r.raise_for_status();ids.append(r.json()['id'])
                suffix='tutor' if profile=='tutor' else 'vet';email='welcome-'+token+'-'+suffix+'@example.invalid';emails.append(email)
                payload={'nome':'Welcome Test Tutor' if profile=='tutor' else 'Welcome Test Vet','email':email,'password':secrets.token_urlsafe(24),'telefone':'11999999999'}
                if profile=='tutor':payload.update(cpf=cpf(),endereco='Rua Teste')
                else:payload.update(crmv='WLR'+token,crmv_uf='SP',especies_ids=[options['especies'][0]['id']],especialidades_ids=[options['especialidades'][0]['id']])
                outcome=call(client,name,payload);assert outcome.get('status')=='exception'
                exists=unpack(call(client,'Notifications/welcome_synthetic_probe',{'email':email,'action':'inspect'}));assert exists.get('exists') is False
                results.append({'profile':profile,'failure_after_event_insertion':True,'identity_rolled_back':True,'welcome_not_dispatched':True})
                print('PASS: rollback após evento, perfil',profile,flush=True)
        finally:
            for email in emails:
                try:
                    value=unpack(call(client,'Notifications/welcome_synthetic_probe',{'email':email,'action':'cleanup'}));cleaned.append(value.get('exists') is False)
                except Exception:cleaned.append(False)
            removed=[]
            for fid in ids:
                time.sleep(3.2);r=client.delete(base+'/function/'+str(fid),params={'branch':'v1'},headers=headers);removed.append(r.status_code in (200,404))
            out={'tests':results,'real_email_sent':False,'cleanup_complete':all(cleaned) and all(removed)}
            (ROOT/'openspec/changes/archive/2026-11-16-enviar-boas-vindas-cadastro/evidence/native-rollback.json').write_text(json.dumps(out,indent=2));assert out['cleanup_complete']
    assert len(results)==2

if __name__=='__main__':main()
