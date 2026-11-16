"""Integração Xano com fixtures sintéticas; entrega simulada apenas na função interna.

Não comprova recebimento de e-mail. Nenhum endpoint de bypass é publicado.
Executar somente no workspace de desenvolvimento definido pela fixture ignorada.
"""
import json
import argparse
import re
import os
from pathlib import Path
import secrets
import sys
import tempfile
import time

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vet_tech.shared.config import get_xano_base_url
from vet_tech.shared.xano_client import AUTH_API_GROUP

FIXTURES = ROOT / '.env.foundation-fixtures.json'
RESULTS = ROOT / 'openspec/changes/archive/2026-11-15-verificar-alteracao-senha-email/evidence/security-live.json'


def save_private(data):
    fd, name = tempfile.mkstemp(prefix='.env.password-save-', dir=ROOT)
    with os.fdopen(fd, 'w') as output:
        json.dump(data, output)
    os.replace(name, FIXTURES)
    FIXTURES.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--purpose', choices=('change', 'reset'))
    parser.add_argument('--actor', choices=('tutor_a', 'vet_a'))
    options = parser.parse_args()
    evidence = RESULTS.with_name('security-live-' + options.purpose + '.json') if options.purpose else RESULTS
    cfg = json.loads(FIXTURES.read_text())
    if cfg.get('environment') != 'development' or cfg.get('synthetic') is not True:
        raise SystemExit('Fixture de desenvolvimento sintética obrigatória.')
    origin = get_xano_base_url()
    if cfg.get('origin', '').rstrip('/') != origin:
        raise SystemExit('Origem da fixture não coincide com a configuração local.')
    if cfg.get('password_test_pending'):
        raise SystemExit('Há uma troca anterior incerta; reconciliar a fixture antes de continuar.')
    credentials = yaml.safe_load((Path.home() / '.xano/credentials.yaml').read_text())
    selected = credentials.get('default_profile', credentials.get('default', next(iter(credentials['profiles']))))
    profile = credentials['profiles'][selected]
    if profile['instance_origin'].rstrip('/') != origin:
        raise SystemExit('Perfil administrativo não coincide com o workspace de teste.')
    base = origin + '/api:' + AUTH_API_GROUP + '/'
    meta = origin + '/api:meta/workspace/' + str(profile['workspace']) + '/function/run'
    results = []
    last_call = 0.0
    with httpx.Client(timeout=35) as client:
        def pace():
            nonlocal last_call
            remaining = 3 - (time.monotonic() - last_call)
            if remaining > 0:
                time.sleep(remaining)
            last_call = time.monotonic()

        def api(label, endpoint, payload, expected=200, token=''):
            pace()
            response = client.post(base + endpoint, json=payload, headers={'Authorization': 'Bearer ' + token} if token else {})
            ok = response.status_code in expected if isinstance(expected, (tuple, list, set)) else response.status_code == expected
            results.append({'check': label, 'status': response.status_code, 'ok': ok})
            evidence.write_text(json.dumps({'delivery': 'simulated_in_internal_function_for_synthetic_accounts_only', 'checks': results}, ensure_ascii=False, indent=2))
            print(label, response.status_code, 'OK' if ok else 'FALHA', flush=True)
            if not ok:
                raise RuntimeError('Falha no cenário ' + label + '; corpos e credenciais ocultados.')
            return response.json()

        def internal(payload):
            pace()
            response = client.post(meta, json={'name': 'Security/password_operation', 'branch': 'v1', 'input': payload}, headers={'Authorization': 'Bearer ' + profile['access_token']})
            if response.status_code != 200:
                raise RuntimeError('Falha na função interna de teste; resposta ocultada.')
            data = response.json()
            if 'result' in data:
                data = data['result']
            while isinstance(data, dict) and 'status' in data:
                if data['status'] != 'ok':
                    diagnostic = json.dumps(data, ensure_ascii=False)
                    known = [s for s in ('Invalid email', 'Invalid input', 'Unable to locate var', 'Unexpected end of JSON input', 'Invalid name', 'required') if s.lower() in diagnostic.lower()]
                    print('Diagnóstico sanitizado:', known or 'erro interno sem classificação', flush=True)
                    print('Variáveis ausentes:', re.findall(r'Unable to locate var: ([A-Za-z_][A-Za-z0-9_.]*)', diagnostic), flush=True)
                    raise RuntimeError('Função interna rejeitou cenário sintético; resposta ocultada.')
                data = data['result']
            if not isinstance(data, dict) or not isinstance(data.get('public'), dict):
                raise RuntimeError('Formato inesperado no teste interno; resposta ocultada.')
            return data

        for actor, domain in (('tutor_a', 'tutor'), ('vet_a', 'veterinario')):
            if options.actor and actor != options.actor:
                continue
            identity_id = cfg['veterinario_a' if actor == 'vet_a' else actor]
            cred = cfg['identity_credentials'][actor]
            if not cred['email'].endswith('.invalid'):
                raise RuntimeError('O harness só permite contas de e-mail .invalid.')
            session = api(domain + ' login inicial', 'acesso/login', cred)
            if session.get('perfil') != domain or str(session.get('identidade_id')) != str(identity_id):
                raise RuntimeError('Identidade da fixture não confirmada.')
            token = session['authToken']
            other = 'veterinario' if domain == 'tutor' else 'tutor'
            api(domain + ' token cruzado', other + '/password/request-code', {'current_password': cred['password']}, 401, token)
            for purpose in ((options.purpose,) if options.purpose else ('change', 'reset')):
                request = {'action': 'request', 'purpose': purpose}
                if purpose == 'change':
                    request.update(profile=domain, actor_id=int(identity_id), current_password=cred['password'])
                else:
                    request['email'] = cred['email']
                issued = internal(request)
                public = issued['public']
                if public.get('ok') is not True or not issued.get('send'):
                    raise RuntimeError('Emissão sintética foi rejeitada ou limitada; não repetir automaticamente.')
                challenge = public['challenge_id']
                code = issued['code']
                assert isinstance(code, str) and len(code) == 6 and code.isascii() and code.isdecimal()
                # Exercitar política real de código/hash; não simular a API pública de envio.
                internal({'action': 'delivery', 'purpose': purpose, 'challenge_id': challenge, 'delivered': True})
                new_password = secrets.token_urlsafe(24)
                if purpose == 'change':
                    wrong = '000000' if code != '000000' else '000001'
                    payload = {'current_password': cred['password'], 'new_password': new_password, 'password_confirmation': new_password, 'challenge_id': challenge, 'code': wrong}
                    api(domain + ' código incorreto', domain + '/password', payload, 400, token)
                    payload['code'] = code
                    endpoint = domain + '/password'
                else:
                    verified = api(domain + ' verificação de recuperação', 'acesso/password-reset/verify', {'challenge_id': challenge, 'code': code})
                    restricted = verified['reset_token']
                    if 'authToken' in verified:
                        raise RuntimeError('Recuperação não pode autenticar usuário.')
                    api(domain + ' replay do código', 'acesso/password-reset/verify', {'challenge_id': challenge, 'code': code}, 400)
                    payload = {'reset_token': restricted, 'new_password': new_password, 'password_confirmation': new_password}
                    endpoint = 'acesso/password-reset/complete'
                cfg['password_test_pending'] = {'actor': actor, 'new_password': new_password}
                save_private(cfg)
                result = api(domain + ' conclusão ' + purpose, endpoint, payload, token=token if purpose == 'change' else '')
                if result.get('success') is not True:
                    raise RuntimeError('Resposta de conclusão inválida; reconciliar fixture pendente.')
                previous = cred['password']
                cred['password'] = new_password
                cfg.pop('password_test_pending')
                save_private(cfg)
                api(domain + ' senha anterior rejeitada ' + purpose, 'acesso/login', {'email': cred['email'], 'password': previous}, (401, 403))
                session = api(domain + ' senha nova aceita ' + purpose, 'acesso/login', cred)
                token = session['authToken']
                cfg.setdefault('tokens', {})[actor] = token
                save_private(cfg)
                if purpose == 'change':
                    payload['current_password'] = new_password
                api(domain + ' replay da conclusão ' + purpose, endpoint, payload, 400, token if purpose == 'change' else '')
    evidence.write_text(json.dumps({'delivery': 'simulated_in_internal_function_for_synthetic_accounts_only', 'checks': results}, ensure_ascii=False, indent=2))
    print('Integração de política concluída; entrega de e-mail não comprovada por este harness.')


if __name__ == '__main__':
    main()
