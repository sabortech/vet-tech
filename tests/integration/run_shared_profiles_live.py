"""Real shared-profile checks, restricted to an explicitly named ephemeral tenant.

--prepare writes fixture functions to ignored .venv/shared-profile-test-backend.
Push that directory to the ephemeral tenant before running --run.
Never uses Metadata table writes or production identities. Fixture credentials
stay in .venv/shared-profile-fixtures.json for optional browser QA.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import secrets
import shutil
import sys
import time
import uuid

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.profile_migration_inventory import cli_profile

FIXTURE_NAME = "Verification/shared_profiles_seed"
REPORT_NAME = "Verification/shared_profiles_records"
RESET_NAME = "Verification/shared_profiles_reset"
EDGES_NAME = "Verification/shared_profiles_edges"
FIXTURES = ROOT / ".venv/shared-profile-fixtures.json"
VERIFIER = ROOT / ".venv/shared-profile-verifier.json"


def prepare():
    target = ROOT / ".venv/shared-profile-test-backend"
    shutil.copytree(ROOT / "xano", target, dirs_exist_ok=True)
    folder = target / "function/verification"
    folder.mkdir(parents=True, exist_ok=True)
    specialties = json.loads((ROOT / "xano/seed/especialidades.json").read_text(encoding="utf-8"))
    seed = ['function "' + FIXTURE_NAME + '" {', '  input {}', '  stack {']
    for index, name in enumerate(("Cachorro", "Gato")):
        seed.append('    db.add especie { data = {nome: ' + json.dumps(name) + '} } as $species' + str(index))
    for index, record in enumerate(specialties):
        seed.append('    db.add especialidade { data = ' + json.dumps(record, ensure_ascii=False) + ' } as $specialty' + str(index))
    seed.extend(['  }', '  response = {seeded: true}', '}'])
    (folder / "seed.xs").write_text('\n'.join(seed) + '\n', encoding="utf-8")
    report = ['function "' + REPORT_NAME + '" {', '  input {}', '  stack {']
    projections = {"tutor": ["id", "email"], "veterinario": ["id", "email", "crmv", "crmv_uf", "clinica_id"],
                   "reserva_email": ["id", "email", "perfil", "identidade_id"], "especie": ["id", "nome"],
                   "especialidade": ["id", "nome"], "veterinario_especie": ["id", "veterinario_id", "especie_id"],
                   "veterinario_especialidade": ["id", "veterinario_id", "especialidade_id"]}
    for table, fields in projections.items():
        report.extend(['    db.query ' + table + ' {', '      output = ' + json.dumps(fields),
                       '      return = {type: "list"}', '    } as $' + table])
    report.extend(['  }', '  response = {' + ', '.join(table + ': $' + table for table in projections) + '}', '}'])
    (folder / "records.xs").write_text('\n'.join(report) + '\n', encoding="utf-8")
    # Some hosted clusters do not implement tenant Metadata table/function APIs.
    # Capability-protected routes exist ONLY in the ignored ephemeral bundle.
    verifier = json.loads(VERIFIER.read_text()) if VERIFIER.exists() else {"token": secrets.token_urlsafe(32)}
    VERIFIER.write_text(json.dumps(verifier), encoding="utf-8")
    api = target / 'api/verification'
    api.mkdir(parents=True, exist_ok=True)
    (api / 'group.xs').write_text('api_group Verification {\n  canonical = "vt-profile-checks"\n}\n', encoding='utf-8')
    reset = ['function "'+RESET_NAME+'" {', '  input {}', '  stack {']
    for table in ('tutor', 'veterinario', 'reserva_email', 'pet'):
        marker_field = 'nome' if table == 'pet' else 'email'
        reset.extend(['    db.query '+table+' {', '      output = ["id", "'+marker_field+'"]',
                      '      return = {type: "list"}', '    } as $'+table,
                      '    foreach ($'+table+') {', '      each as $row {',
                      '        precondition ("/^vt-profiles-/"|regex_matches:$row.'+marker_field+') {',
                      '          error_type = "accessdenied"', '          error = "Unknown record: reset refused."',
                      '        }', '      }', '    }'])
    for table in ('pet', 'veterinario_especie', 'veterinario_especialidade', 'reserva_email', 'veterinario', 'tutor'):
        reset.extend(['    db.query '+table+' {', '      output = ["id"]',
                      '      return = {type: "list"}', '    } as $all_'+table,
                      '    foreach ($all_'+table+') {', '      each as $record {',
                      '        db.del '+table+' {', '          field_name = "id"',
                      '          field_value = $record.id', '        }', '      }', '    }'])
    reset.extend(['  }', '  response = {reset: true}', '}'])
    (folder / 'reset.xs').write_text('\n'.join(reset)+'\n', encoding='utf-8')
    edges = '''function "Verification/shared_profiles_edges" {
  input {
    text action
    email email
  }
  stack {
    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id", "email"]
    } as $first_tutor
    precondition ("/^vt-profiles-/"|regex_matches:$first_tutor.email) {
      error_type = "accessdenied"
      error = "Unknown fixture."
    }
    var $edge_result { value = {} }
    conditional {
      if ($input.action == "expired") {
        security.create_auth_token {
          table = "tutor"
          id = $first_tutor.id
          expiration = 1
          extras = {}
        } as $short_token
        var.update $edge_result { value = {authToken: $short_token} }
      }
      elseif ($input.action == "ambiguity") {
        db.add veterinario {
          data = {nome: "Fixture ambiguity", email: $first_tutor.email, senha: "ephemeral-synthetic-only"}
        } as $duplicate
        var.update $edge_result { value = {injected: true} }
      }
      elseif ($input.action == "cleanup") {
        db.query veterinario {
          where = $db.veterinario.nome == "Fixture ambiguity"
          output = ["id"]
          return = {type: "list"}
        } as $duplicates
        foreach ($duplicates) {
          each as $duplicate {
            db.del veterinario {
              field_name = "id"
              field_value = $duplicate.id
            }
          }
        }
        var.update $edge_result { value = {cleaned: true} }
      }
    }
  }
  response = $edge_result
}
'''
    (folder / 'edges.xs').write_text(edges, encoding='utf-8')
    for route, name in [('seed', FIXTURE_NAME), ('records', REPORT_NAME), ('reset', RESET_NAME), ('edges', EDGES_NAME)]:
        action_input = '\n    text action\n    email email' if name == EDGES_NAME else ''
        function_input = '{action: $input.action, email: $input.email}' if name == EDGES_NAME else '{}'
        source = ('query "'+route+'" verb=POST {\n  api_group = "Verification"\n'
                  '  input {\n    text verifier_token'+action_input+'\n  }\n  stack {\n'
                  '    precondition ($input.verifier_token == '+json.dumps(verifier['token'])+') {\n'
                  '      error_type = "accessdenied"\n      error = "Not available."\n    }\n'
                  '    function.run "'+name+'" { input = '+function_input+' } as $result\n  }\n  response = $result\n}\n')
        (api / (route+'_POST.xs')).write_text(source, encoding='utf-8')
    print("Fixture functions prepared under ignored .venv/shared-profile-test-backend; no network writes.")


def cpf():
    digits = [secrets.randbelow(10) for _ in range(9)]
    for length in (9, 10):
        rem = sum(d * w for d, w in zip(digits, range(length + 1, 1, -1))) % 11
        digits.append(0 if rem < 2 else 11 - rem)
    return ''.join(map(str, digits))


class Verification:
    def __init__(self, tenant):
        if not tenant or not tenant.startswith("ex"):
            raise RuntimeError("An ephemeral tenant name starting with ex is required")
        profile = cli_profile()
        self.tenant = tenant
        self.origin = profile["instance_origin"].rstrip('/')
        # Confirm the target type at the control plane before any fixture write.
        with httpx.Client(timeout=40, headers={"Authorization":"Bearer "+profile["access_token"]}) as metadata:
            target = metadata.get(self.origin+'/api:meta/workspace/'+str(profile['workspace'])+'/tenant/'+tenant)
        if not target.is_success or target.json().get('type') != 'ephemeral' or target.json().get('name') != tenant:
            raise RuntimeError('The control plane did not confirm an ephemeral test tenant; refusing fixture writes')
        self.api = httpx.Client(timeout=60, headers={"X-Tenant": tenant})
        self.marker = "vt-profiles-" + uuid.uuid4().hex[:12]
        self.checks = []

    def call(self, method, url, **kwargs):
        # Repeat only explicit rate-limit rejections, never uncertain POSTs.
        for attempt in range(7):
            result = self.api.request(method, url, **kwargs)
            if result.status_code != 429:
                return result
            time.sleep(min(2 ** attempt, 8))
        raise RuntimeError('Rate limit persisted in the test tenant')

    def function(self, name, **inputs):
        verifier = json.loads(VERIFIER.read_text(encoding='utf-8'))
        route = {FIXTURE_NAME:'seed', REPORT_NAME:'records', RESET_NAME:'reset', EDGES_NAME:'edges'}[name]
        r = self.call('POST', self.origin+'/api:vt-profile-checks/'+route, json={'verifier_token':verifier['token'], **inputs})
        if not r.is_success:
            raise RuntimeError(f"Fixture function failed: HTTP {r.status_code}")
        body = r.json()
        if body.get("status", "ok") != "ok":
            # Fixture functions contain no credentials; keep diagnostics private.
            (ROOT / '.venv/shared-profile-error.json').write_text(json.dumps(body), encoding='utf-8')
            raise RuntimeError("Fixture function returned an error; private diagnostic saved")
        return body.get('result', body)

    def request(self, method, endpoint, payload=None, token=None):
        headers = {"Authorization": "Bearer " + token} if token else {}
        return self.call(method, self.origin + '/api:H62nB-j2/' + endpoint, json=payload, headers=headers)

    def note(self, name):
        self.checks.append(name)
        print(json.dumps({"scenario": name, "status": "passed"}), flush=True)

    def tutor(self, suffix, email=None):
        return {"nome": "Fixture tutor", "email": email or f'{self.marker}-{suffix}@example.invalid',
                "telefone": "11999999999", "endereco": "Fictitious test address", "cpf": cpf(),
                "password": secrets.token_urlsafe(24)}

    def veterinarian(self, suffix, options, email=None):
        return {"nome": "Fixture veterinario", "email": email or f'{self.marker}-{suffix}@example.invalid',
                "telefone": "11999999999", "password": secrets.token_urlsafe(24),
                "crmv": "V" + secrets.token_hex(5).upper(), "crmv_uf": "SP", "clinica_id": None,
                "especies_ids": [item["id"] for item in options['especies']],
                "especialidades_ids": [options['especialidades'][0]['id']]}

    def run(self):
        initial = self.function(REPORT_NAME)
        if initial.get('tutor') or initial.get('veterinario'):
            raise RuntimeError("Test tenant must start without identities; refusing to reuse unknown accounts")
        if not initial['especie']:
            self.function(FIXTURE_NAME)
        r = self.request('GET', 'cadastro/opcoes')
        assert r.status_code == 200, f"Public options: HTTP {r.status_code}"
        options = r.json()
        assert len(options['especies']) >= 2 and options['especialidades']
        assert all(set(row) == {'id', 'nome'} for key in options for row in options[key])
        self.note('public_catalog_projection')
        tutor = self.tutor('tutor')
        vet = self.veterinarian('vet', options)
        FIXTURES.write_text(json.dumps({'tenant':self.tenant,'origin':self.origin,'tutor':tutor,'vet':vet,'checks':self.checks}), encoding='utf-8')
        assert self.request('POST', 'tutor/signup', tutor).status_code == 200
        assert self.request('POST', 'veterinario/signup', vet).status_code == 200
        self.note('both_signups_and_optional_clinic')
        tokens, identities = {}, {}
        for profile, account in [('tutor', tutor), ('veterinario', vet)]:
            r = self.request('POST', 'acesso/login', {key: account[key] for key in ('email','password')})
            assert r.status_code == 200, f"Shared login {profile}: HTTP {r.status_code}"
            result = r.json()
            assert result['perfil'] == profile and result['authToken']
            tokens[profile] = result['authToken']
            identities[profile] = result['identidade_id']
            r = self.request('GET', profile+'/me', token=tokens[profile])
            assert r.status_code == 200 and r.json()['identidade_id'] == identities[profile]
        assert identities['tutor'] == identities['veterinario'], 'Fixture IDs must coincide to test table isolation'
        self.note('shared_login_me_and_coincident_ids')
        assert self.request('GET','tutor/me', token=tokens['veterinario']).status_code == 401
        assert self.request('GET','veterinario/me', token=tokens['tutor']).status_code == 401
        r = self.call('GET', self.origin+'/api:vettech-pets/pets', params={'perfil':'tutor'}, headers={'Authorization':'Bearer '+tokens['veterinario']})
        assert r.status_code == 401
        self.note('cross_tokens_and_forged_profile_rejected')
        for account in [tutor, vet]:
            invalid = self.request('POST','acesso/login',{'email':account['email'],'password':'wrong'})
            assert invalid.status_code in (401, 403), f"Invalid credentials: HTTP {invalid.status_code}"
        assert self.request('GET','tutor/me').status_code == 401
        self.note('invalid_credentials_and_missing_token')
        assert self.request('POST','veterinario/signup',self.veterinarian('duplicate',options,email=tutor['email'])).status_code >= 400
        assert self.request('POST','tutor/signup',self.tutor('duplicate',email=vet['email'])).status_code >= 400
        self.note('global_email_uniqueness_in_both_directions')
        duplicate_crmv = self.veterinarian('rollback', options)
        duplicate_crmv.update(crmv=vet['crmv'], crmv_uf=vet['crmv_uf'])
        assert self.request('POST','veterinario/signup',duplicate_crmv).status_code >= 400
        report = self.function(REPORT_NAME)
        assert not any(row['email'] == duplicate_crmv['email'] for row in report['reserva_email'])
        assert not any(row['email'] == duplicate_crmv['email'] for row in report['veterinario'])
        self.note('late_unique_failure_rolls_back_email_and_identity')
        for invalid in [dict(vet, crmv='BAD!'), dict(vet, crmv_uf='XX'), dict(vet, especies_ids=[]),
                        dict(vet, especies_ids=[9999999]), dict(vet, especialidades_ids=[9999999]), dict(vet, clinica_id=9999999)]:
            invalid['email'] = f'{self.marker}-{secrets.token_hex(5)}@example.invalid'
            assert self.request('POST','veterinario/signup',invalid).status_code >= 400
        self.note('professional_validation_and_invalid_catalog_links')
        email = f'{self.marker}-race@example.invalid'
        race_tutor, race_vet = self.tutor('race', email), self.veterinarian('race', options, email)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.request,'POST','tutor/signup',race_tutor), pool.submit(self.request,'POST','veterinario/signup',race_vet)]
            responses = [f.result() for f in futures]
        assert sum(r.status_code == 200 for r in responses) == 1, 'Concurrent signups must have exactly one winner'
        report = self.function(REPORT_NAME)
        assert sum(row['email'] == email for row in report['tutor'] + report['veterinario']) == 1
        assert sum(row['email'] == email for row in report['reserva_email']) == 1
        self.note('concurrent_email_reservation_has_one_winner')
        legacy = self.request('POST','tutor/login',{key:tutor[key] for key in ('email','password')})
        assert legacy.status_code == 200 and set(legacy.json()) == {'authToken','tutor_id'}
        self.note('legacy_tutor_login_preserved')
        FIXTURES.write_text(json.dumps({'tenant':self.tenant,'origin':self.origin,'tutor':tutor,'vet':vet,'tokens':tokens,'checks':self.checks}), encoding='utf-8')
        print(json.dumps({'passed':len(self.checks),'fixture_file':str(FIXTURES.relative_to(ROOT))}))

    def edges(self):
        data = json.loads(FIXTURES.read_text(encoding='utf-8'))
        assert data['tenant'] == self.tenant
        email = data['tutor']['email']
        short_token = self.function(EDGES_NAME, action='expired', email=email)['authToken']
        time.sleep(2)
        assert self.request('GET','tutor/me',token=short_token).status_code == 401
        self.note('expired_token_rejected')
        self.function(EDGES_NAME, action='ambiguity', email=email)
        try:
            r = self.request('POST','acesso/login',{key:data['tutor'][key] for key in ('email','password')})
            assert r.status_code in (401,403) and not r.json().get('authToken')
            self.note('preexisting_cross_profile_ambiguity_denies_login')
        finally:
            self.function(EDGES_NAME, action='cleanup', email=email)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--tenant')
    parser.add_argument('--reset-fixtures',action='store_true',help='Delete only marker-validated synthetic identities in the ephemeral tenant')
    parser.add_argument('--edges-only',action='store_true')
    args=parser.parse_args()
    if args.prepare:
        prepare()
    if args.run or args.reset_fixtures or args.edges_only:
        try:
            verification = Verification(args.tenant)
            if args.reset_fixtures:
                verification.function(RESET_NAME)
                print('Ephemeral marker-validated identity fixtures removed; catalog fixtures preserved.')
            if args.run:
                verification.run()
            if args.edges_only:
                verification.edges()
        except Exception as error:
            # Never dump requests, tokens or account dictionaries.
            print(f'Live verification stopped: {type(error).__name__}: {error}',file=sys.stderr)
            raise SystemExit(1)
