"""Test only existing, marker-validated synthetic development accounts.

The synthetic veterinarian's password is rotated and persisted in the ignored
fixture file immediately after success. No real user or clinical record is used.
"""
import argparse
import json
from pathlib import Path
import secrets
import sys
import time

import httpx
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vet_tech.shared.config import get_xano_base_url
from vet_tech.shared.xano_client import AUTH_API_GROUP

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fixtures', type=Path, default=ROOT/'.env.foundation-fixtures.json')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
config = json.loads(args.fixtures.read_text())
assert config['environment'] == 'development' and config['synthetic'] is True
assert config['origin'].rstrip('/') == get_xano_base_url()
credentials = config['identity_credentials']
for key in ('vet_a', 'vet_b', 'tutor_a'):
    assert credentials[key]['email'].endswith('@example.invalid'), 'Only synthetic accounts accepted'
results = []
last_call = 0.0


def call(method, route, payload=None, token=None, expected=(200,)):
    global last_call
    time.sleep(max(0, 2.8-(time.monotonic()-last_call)))
    last_call = time.monotonic()
    r = client.request(method, '/api:'+AUTH_API_GROUP+'/'+route, json=payload,
                       headers={'Authorization': 'Bearer '+token} if token else {})
    assert r.status_code in expected, f'{method} {route}: unexpected HTTP {r.status_code}'
    return r.json() if r.is_success else None


def note(text):
    results.append(text)
    print(json.dumps({'scenario': text, 'status': 'passed'}, ensure_ascii=False), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')


with httpx.Client(base_url=config['origin'], timeout=35) as client:
    a = call('POST', 'acesso/login', credentials['vet_a'])
    b = call('POST', 'acesso/login', credentials['vet_b'])
    tutor = call('POST', 'acesso/login', credentials['tutor_a'])
    assert a['perfil'] == b['perfil'] == 'veterinario' and tutor['perfil'] == 'tutor'
    before_a = call('GET', 'veterinario/account', token=a['authToken'])
    before_b = call('GET', 'veterinario/account', token=b['authToken'])
    assert set(before_a) == {'nome','email','telefone','crmv','crmv_uf'}
    assert before_a['email'] == credentials['vet_a']['email']
    assert before_a['nome'].strip() and before_a['telefone'].strip(), 'Synthetic fixture requires complete account fields before reversible tests'
    call('GET', 'veterinario/account', expected=(401,403))
    call('GET', 'veterinario/account', token='invalid-token', expected=(401,403))
    call('GET', 'veterinario/account', token=tutor['authToken'], expected=(401,403))
    call('PATCH', 'veterinario/account', {'nome':'Forbidden','telefone':'123'}, tutor['authToken'], expected=(401,403))
    call('POST', 'veterinario/password', {'current_password':'wrong','new_password':'x','password_confirmation':'x'}, tutor['authToken'], expected=(401,403))
    tutor_before = call('GET', 'tutor/account', token=tutor['authToken'])
    call('GET', 'tutor/account', token=a['authToken'], expected=(401,403))
    note('Published endpoints: own-account projection and cross-profile/unauthenticated rejection')
    changed = False
    try:
        updated = call('PATCH', 'veterinario/account', {
            'nome': '  Fixture configurações médica  ', 'telefone': before_a['telefone'],
            'id': b['identidade_id'], 'veterinario_id': b['identidade_id'],
            'email': before_b['email'], 'crmv':'FORGED', 'crmv_uf':'XX', 'clinica_id':999999,
            'especies_ids':[999999], 'especialidades_ids':[999999], 'senha':'forged', 'password':'forged'}, a['authToken'])
        changed = True
        assert updated == {**before_a, 'nome':'Fixture configurações médica'}
        assert call('GET', 'veterinario/account', token=b['authToken']) == before_b
        call('PATCH', 'veterinario/account', {'nome':'invalid', 'telefone':'  '}, a['authToken'], expected=(400,422))
        assert call('GET', 'veterinario/account', token=a['authToken']) == updated
        note('Allowlist and validation: protected fields and other veterinarian preserved; no partial write')
    finally:
        if changed:
            restored = call('PATCH', 'veterinario/account', {'nome':before_a['nome'], 'telefone':before_a['telefone']}, a['authToken'])
            assert restored == before_a
    call('POST', 'veterinario/password', {'current_password':'wrong', 'new_password':'x', 'password_confirmation':'x'}, a['authToken'], expected=(400,422))
    call('POST', 'veterinario/password', {'current_password':credentials['vet_a']['password'], 'new_password':'x', 'password_confirmation':'y'}, a['authToken'], expected=(400,422))
    old_password = credentials['vet_a']['password']
    new_password = ' '+secrets.token_urlsafe(24)+' '
    result = call('POST', 'veterinario/password', {'current_password':old_password,'new_password':new_password,'password_confirmation':new_password}, a['authToken'])
    assert result == {'success':True}
    credentials['vet_a']['password'] = new_password
    args.fixtures.write_text(json.dumps(config))
    args.fixtures.chmod(0o600)
    call('POST', 'acesso/login', {'email':credentials['vet_a']['email'],'password':old_password}, expected=(401,403))
    login = call('POST', 'acesso/login', credentials['vet_a'])
    assert login['perfil'] == 'veterinario' and login['identidade_id'] == a['identidade_id']
    assert call('GET', 'veterinario/account', token=login['authToken']) == before_a
    assert call('GET', 'tutor/account', token=tutor['authToken']) == tutor_before
    assert call('POST','acesso/login',credentials['vet_b'])['identidade_id'] == b['identidade_id']
    note('Password: current/confirmation checked; hash accepts exact new password, rejects old; other accounts unchanged')
