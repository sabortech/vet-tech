"""Casos de borda reais usando apenas metadados técnicos de fixtures sintéticas.

Ajusta o relógio dos desafios pelo Metadata API para testar expiração sem esperar
10 minutos. Não altera senhas nem envia e-mails; entrega é simulada internamente.
"""
import copy
import hashlib
import hmac
import secrets
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import time
import httpx
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vet_tech.shared.config import get_xano_base_url
from vet_tech.shared.xano_client import AUTH_API_GROUP


def main():
    cfg = json.loads((ROOT / '.env.foundation-fixtures.json').read_text())
    assert cfg['synthetic'] is True and cfg['environment'] == 'development'
    origin = get_xano_base_url()
    assert cfg['origin'].rstrip('/') == origin
    credentials = yaml.safe_load((Path.home() / '.xano/credentials.yaml').read_text())
    profile = credentials['profiles'][credentials.get('default_profile', credentials.get('default', next(iter(credentials['profiles']))))]
    assert profile['instance_origin'].rstrip('/') == origin
    meta = origin + '/api:meta/workspace/' + str(profile['workspace'])
    base = origin + '/api:' + AUTH_API_GROUP + '/'
    headers = {'Authorization': 'Bearer ' + profile['access_token']}
    checks = []
    evidence = ROOT / 'openspec/changes/verificar-alteracao-senha-email/evidence/security-edges.json'
    if '--grant-only' in sys.argv:
        evidence = evidence.with_name('security-concurrency.json')
    last_call = 0
    with httpx.Client(timeout=40) as client:
        def pace():
            nonlocal last_call
            time.sleep(max(0, 3 - (time.monotonic() - last_call)))
            last_call = time.monotonic()

        def admin(method, path, **kwargs):
            pace()
            r = client.request(method, meta + path, headers=headers, **kwargs)
            if r.status_code != 200:
                raise RuntimeError('Metadata recusou operação de teste; resposta ocultada.')
            return r.json()

        def internal(payload):
            data = admin('POST', '/function/run', json={'name': 'Security/password_operation', 'branch': 'v1', 'input': payload})
            if 'result' in data:
                data = data['result']
            while isinstance(data, dict) and 'status' in data:
                if data['status'] != 'ok':
                    raise RuntimeError('Falha interna; resposta ocultada.')
                data = data['result']
            return data

        def record(label, ok, status=None):
            checks.append({'check': label, 'ok': bool(ok), **({'status': status} if status is not None else {})})
            evidence.write_text(json.dumps({'delivery': 'simulated', 'clock': 'technical_fixture_metadata_only', 'checks': checks}, ensure_ascii=False, indent=2))
            print(label, 'OK' if ok else 'FALHA', flush=True)
            if not ok:
                raise RuntimeError('Falha no cenário: ' + label)

        def api(label, path, payload, expected=400, token=''):
            pace()
            r = client.post(base + path, json=payload, headers={'Authorization': 'Bearer ' + token} if token else {})
            record(label, r.status_code == expected, r.status_code)
            return r

        tables = admin('GET', '/table', params={'search': 'password_challenge', 'per_page': 100})
        items = tables if isinstance(tables, list) else tables['items']
        table = next(t for t in items if t['name'] == 'password_challenge')
        content = '/table/' + str(table['id']) + '/content'
        cred = cfg['identity_credentials']['tutor_b']
        assert cred['email'].endswith('.invalid')
        session = api('login fixture sem etapa adicional', 'acesso/login', cred, 200).json()
        assert session['perfil'] == 'tutor' and session['identidade_id'] == cfg['tutor_b']
        token = session['authToken']

        def issue(purpose):
            payload = {'action': 'request', 'purpose': purpose}
            if purpose == 'change':
                payload.update(profile='tutor', actor_id=cfg['tutor_b'], current_password=cred['password'])
            else:
                payload['email'] = cred['email']
            issued = internal(payload)
            record('emissão interna ' + purpose, issued.get('send') is True and issued['public']['ok'] is True)
            challenge = issued['public']['challenge_id']
            internal({'action': 'delivery', 'purpose': purpose, 'challenge_id': challenge, 'delivered': True})
            return challenge, issued['code']

        def get_row(challenge):
            data = admin('GET', content, params={'per_page': 100})
            rows = data if isinstance(data, list) else data['items']
            row = next(r for r in rows if r['public_id'] == challenge)
            assert row['profile'] == 'tutor' and row['identity_id'] == cfg['tutor_b']
            return row

        def update(row, state):
            assert row['identity_id'] == cfg['tutor_b'] and row['profile'] == 'tutor'
            updated = {**row, 'state': state}
            admin('PUT', content + '/' + str(row['id']), json=updated)

        if '--grant-only' not in sys.argv:
            challenge, code = issue('change')
            row = get_row(challenge)
            original = copy.deepcopy(row['state'])
            payload = {'current_password': cred['password'], 'new_password': 'not-committed-test', 'password_confirmation': 'not-committed-test', 'challenge_id': challenge, 'code': code}
            state = copy.deepcopy(original);state['challenge']['expires'] = int(time.time() * 1000) - 1000
            update(row, state)
            api('código expirado rejeitado', 'tutor/password', payload, token=token)
            update(row, original)
            api('finalidade incorreta rejeitada', 'acesso/password-reset/verify', {'challenge_id': challenge, 'code': code})
            other = api('login outra fixture', 'acesso/login', cfg['identity_credentials']['tutor_a'], 200).json()
            api('código de outra conta rejeitado', 'tutor/password', {**payload, 'current_password': cfg['identity_credentials']['tutor_a']['password']}, token=other['authToken'])
            wrong = '000000' if code != '000000' else '000001'
            for i in range(5):
                api('tentativa inválida ' + str(i + 1), 'tutor/password', {**payload, 'code': wrong}, token=token)
            api('código correto após cinco erros rejeitado', 'tutor/password', payload, token=token)
            after = get_row(challenge)
            record('contador persiste após respostas HTTP 400', after['state']['challenge']['attempts'] == 5)
            # Somente o relógio da fixture é recuado para ensaiar reenvio sem espera.
            state = copy.deepcopy(after['state']);state['sends'] = [int(time.time()*1000)-61000]
            update(after, state)
            replacement, replacement_code = issue('change')
            api('desafio substituído rejeitado', 'tutor/password', payload, token=token)
            # Bloqueio de reenvio imediato, sem chamada ao provedor.
            denied = internal({'action': 'request', 'purpose': 'change', 'profile': 'tutor', 'actor_id': cfg['tutor_b'], 'current_password': cred['password']})
            record('intervalo mínimo de reenvio aplicado', denied['public']['ok'] is False and denied['send'] is False)
            row = get_row(replacement);state = copy.deepcopy(row['state'])
            state['sends'] = [int(time.time()*1000)-61000-i*1000 for i in range(5)]
            update(row, state)
            denied = internal({'action': 'request', 'purpose': 'change', 'profile': 'tutor', 'actor_id': cfg['tutor_b'], 'current_password': cred['password']})
            record('limite de cinco envios por hora aplicado', denied['public']['ok'] is False and denied['send'] is False)
        if '--grant-only' in sys.argv:
            # Preparação administrativa limitada à fixture: não zera quotas nem
            # chama o provedor. Isola a concorrência do limite de emissão.
            data = admin('GET', content, params={'per_page': 100})
            rows = data if isinstance(data, list) else data['items']
            row = next(r for r in rows if r['profile'] == 'tutor' and r['identity_id'] == cfg['tutor_b'] and r['state']['purpose'] == 'reset')
            challenge = row['public_id']
            code = str(secrets.randbelow(1000000)).zfill(6)
            secret = dotenv_values(ROOT / '.env')['PASSWORD_CODE_SECRET']
            state = copy.deepcopy(row['state'])
            state['challenge'] = {'digest': hmac.new(secret.encode(), (challenge + ':' + code).encode(), hashlib.sha256).hexdigest(), 'expires': int(time.time()*1000)+600000, 'attempts': 0, 'sent': True, 'consumed': False}
            state['grant'] = None
            update(row, state)
        else:
            challenge, code = issue('reset')
        # Duas confirmações reais disputam o mesmo código. Nenhuma altera senha.
        def verify(_):
            with httpx.Client(timeout=40) as parallel:
                return parallel.post(base + 'acesso/password-reset/verify', json={'challenge_id': challenge, 'code': code})
        pace()
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(verify, (0, 1)))
        statuses = sorted(r.status_code for r in responses)
        print('HTTPs concorrentes:', statuses, flush=True)
        checks.append({'check': 'status das confirmações concorrentes', 'statuses': statuses, 'ok': statuses.count(200) == 1})
        record('verificação concorrente tem um único vencedor', statuses == [200, 400])
        grant = next(r.json()['reset_token'] for r in responses if r.status_code == 200)
        pace()
        r = client.get(base + 'tutor/me', headers={'Authorization': 'Bearer ' + grant})
        record('autorização restrita não autentica sessão', r.status_code == 401, r.status_code)
        row = get_row(challenge);state = copy.deepcopy(row['state']);state['grant']['expires'] = int(time.time()*1000)-1000
        update(row, state)
        api('autorização expirada rejeitada', 'acesso/password-reset/complete', {'reset_token': grant, 'new_password': 'not-committed-test', 'password_confirmation': 'not-committed-test'})
        api('senha original permanece válida', 'acesso/login', cred, 200)
    print('Casos de borda concluídos; nenhuma senha alterada e nenhum e-mail enviado.')


if __name__ == '__main__':
    main()
