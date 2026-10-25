"""Deployment smoke with marker-validated temporary accounts and cleanup.

Requires --allow-temporary-accounts and the private baseline snapshot. Never
prints credentials, changes existing accounts or creates clinical records.
"""
import argparse
import json
from pathlib import Path
import secrets
import sys
import time
import uuid

import httpx

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.profile_migration_inventory import cli_profile, digest, read_pages
from run_shared_profiles_live import cpf


def run(snapshot_path):
    snapshot=json.loads(snapshot_path.read_text(encoding='utf-8'))
    profile=cli_profile()
    assert snapshot['workspace']==profile['workspace']
    base=profile['instance_origin'].rstrip('/')
    meta_base=base+'/api:meta/workspace/'+str(profile['workspace'])
    marker='vt-smoke-'+uuid.uuid4().hex[:12]
    accounts=[]
    private=ROOT/'.venv/shared-profile-smoke.json'
    checks=[]
    with httpx.Client(timeout=40,headers={'Authorization':'Bearer '+profile['access_token']}) as meta, httpx.Client(timeout=40) as api:
        tables={r['name']:r['id'] for r in read_pages(meta,meta_base+'/table')}
        def records(table):
            return read_pages(meta,f'{meta_base}/table/{tables[table]}/content')
        def request(method,endpoint,**kwargs):
            for attempt in range(7):
                r=api.request(method,base+endpoint,**kwargs)
                if r.status_code!=429:
                    return r
                time.sleep(min(2**attempt,8))
            raise RuntimeError('Rate limit persisted')
        def note(name):
            checks.append(name)
            print(json.dumps({'scenario':name,'status':'passed'}),flush=True)
        def cleanup():
            emails={a['email'] for a in accounts}
            owned_tutors=[r for r in records('tutor') if r.get('email') in emails]
            owned_vets=[r for r in records('veterinario') if r.get('email') in emails]
            tutor_ids={r['id'] for r in owned_tutors}
            vet_ids={r['id'] for r in owned_vets}
            assert not any(r.get('tutor_id') in tutor_ids for r in records('pet')), 'Unexpected fixture pet: cleanup refused'
            for table,field in [('veterinario_especie','especie_id'),('veterinario_especialidade','especialidade_id')]:
                for row in records(table):
                    if row['veterinario_id'] in vet_ids:
                        r=meta.delete(f'{meta_base}/table/{tables[table]}/content/{row["id"]}')
                        assert r.is_success, 'Fixture link cleanup failed'
            for table,rows in [('reserva_email',[r for r in records('reserva_email') if r.get('email') in emails]),
                               ('veterinario',owned_vets),('tutor',owned_tutors)]:
                for row in rows:
                    assert str(row['email']).startswith(marker+'-'), 'Foreign row: cleanup refused'
                    r=meta.delete(f'{meta_base}/table/{tables[table]}/content/{row["id"]}')
                    assert r.is_success, 'Fixture identity cleanup failed'
        try:
            r=request('GET','/api:H62nB-j2/cadastro/opcoes')
            assert r.status_code==200
            options=r.json()
            assert options['especies'] and len(options['especialidades'])==5
            assert all(set(item)=={'id','nome'} for key in options for item in options[key])
            note('published_catalogs')
            for role in ('tutor','veterinario'):
                account={'nome':'Fixture smoke','email':marker+'-'+role+'@example.invalid',
                         'telefone':'11999999999','password':secrets.token_urlsafe(24)}
                if role=='tutor':
                    account.update(cpf=cpf(),endereco='Fictitious test address')
                else:
                    account.update(crmv='S'+secrets.token_hex(5).upper(),crmv_uf='SP',clinica_id=None,
                                   especies_ids=[options['especies'][0]['id']],especialidades_ids=[options['especialidades'][0]['id']])
                accounts.append(account)
                private.write_text(json.dumps({'marker':marker,'accounts':accounts}),encoding='utf-8')
                r=request('POST','/api:H62nB-j2/'+role+'/signup',json=account)
                assert r.status_code==200 and r.json()=={'success':True}, 'Published signup failed'
                r=request('POST','/api:H62nB-j2/acesso/login',json={k:account[k] for k in ('email','password')})
                assert r.status_code==200
                login=r.json()
                assert login['perfil']==role
                token=login['authToken']
                r=request('GET','/api:H62nB-j2/'+role+'/me',headers={'Authorization':'Bearer '+token})
                assert r.status_code==200 and r.json()['identidade_id']==login['identidade_id']
                other='veterinario' if role=='tutor' else 'tutor'
                assert request('GET','/api:H62nB-j2/'+other+'/me',headers={'Authorization':'Bearer '+token}).status_code==401
                if role=='tutor':
                    r=request('POST','/api:H62nB-j2/tutor/login',json={k:account[k] for k in ('email','password')})
                    assert r.status_code==200 and set(r.json())=={'authToken','tutor_id'}
                else:
                    assert request('GET','/api:vettech-pets/pets',headers={'Authorization':'Bearer '+token}).status_code==401
                note('published_'+role+'_signup_login_and_isolation')
        finally:
            cleanup()
        for table,original in snapshot['records'].items():
            assert {str(r['id']):digest(r) for r in records(table)}=={str(r['id']):digest(r) for r in original}, 'Preexisting domain data changed'
        note('fixtures_removed_and_preexisting_records_preserved')
        private.unlink(missing_ok=True)
        report={'checks':checks,'original_counts':{t:len(r) for t,r in snapshot['records'].items()},
                'reservation_count':len(records('reserva_email')),'specialty_count':len(records('especialidade'))}
        (ROOT/'openspec/changes/unificar-acesso-perfis/smoke-result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,required=True)
    p.add_argument('--allow-temporary-accounts',action='store_true',required=True)
    args=p.parse_args()
    try:
        run(args.snapshot)
    except Exception as error:
        print('Published smoke stopped: '+type(error).__name__+'. Inspect the private fixture manifest before repeating.',file=sys.stderr)
        raise SystemExit(1)
