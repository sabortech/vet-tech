"""Verifica o webhook publicado com identidades sintéticas existentes, sem republicar APIs."""
import argparse
import json
import os
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import load_dotenv

load_dotenv('.env')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run', required=True)
args = parser.parse_args()
root = Path('.venv/clinical-smoke').resolve()
folder = (root / args.run).resolve()
if not folder.is_relative_to(root):
    raise SystemExit('Ledger fora da pasta privada')
ledger = json.loads((folder / 'ledger.json').read_text(encoding='utf-8'))
checks = []
cases = [
    ('ordinary_tutor', 'tutor', 'ta', 'Como acesso a lista Meus Pets?', False),
    ('handoff_tutor', 'tutor', 'ta', 'Quero falar com um veterinário humano sobre meu pet. Pode propor o atendimento pelo chat?', True),
    ('no_handoff_visitor', 'visitante', None, 'Quero falar com um veterinário humano pelo chat.', False),
    ('no_handoff_veterinarian', 'veterinario', 'va', 'Quero falar com um veterinário humano pelo chat.', False),
]
with httpx.Client(timeout=90) as client:
    for name, role, actor, message, expected in cases:
        rid, cid = str(uuid4()), str(uuid4())
        headers = {'X-VetTech-Secret': os.environ['N8N_CHAT_WEBHOOK_SECRET']}
        if actor:
            headers['X-VetTech-User-Token'] = ledger['actors'][actor]['token']
        response = client.post(os.environ['N8N_CHAT_WEBHOOK_URL'], headers=headers, json={
            'request_id': rid, 'conversation_id': cid, 'message': message,
            'user': {'authenticated': bool(actor), 'role': role, 'name': None}, 'history': [],
        })
        body = response.json()
        valid = (response.status_code == 200 and body.get('ok') is True
                 and body.get('request_id') == rid and body.get('conversation_id') == cid
                 and isinstance(body.get('reply'), str) and bool(body['reply'].strip())
                 and body.get('error') is None and bool(body.get('handoff')) == expected)
        if expected and valid:
            h = body['handoff']
            valid = set(h) == {'type', 'reason'} and h['type'] == 'veterinary' and 1 <= len(h['reason']) <= 1000
        checks.append({'check': name, 'passed': bool(valid), 'status': response.status_code})
        (folder / 'n8n-handoff-results.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
        print(name, bool(valid), 'HTTP', response.status_code, flush=True)
        if not valid:
            raise SystemExit('Falha no contrato publicado; nenhum conteúdo de resposta foi impresso.')
