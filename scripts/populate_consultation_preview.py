"""Populate only five explicitly requested test reservations for Jessy.

Uses the authenticated Xano CLI profile. No deletion or consent changes.
Default is a read-only plan; --apply creates reservations and retains them.
Private manifest makes repeats resume the same five reservations.
"""
import argparse
from datetime import datetime, date, time, timedelta
import hashlib
import json
from pathlib import Path
import sys
from uuid import uuid4
from zoneinfo import ZoneInfo

from animal_catalog import XanoStore, save as save_json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / '.venv/consultation-filter-population/manifest.json'
TZ = ZoneInfo('America/Sao_Paulo')

def save(data):
    save_json(MANIFEST, data)

def candidates(rows, pet_id, vet_id, day):
    occupied = {int(r['agendada_para']) for r in rows if r.get('agendada_para') and
                (r.get('pet_id') == pet_id or r.get('veterinario_id') == vet_id)}
    start = datetime.combine(day, time(8), TZ)
    return [int((start + timedelta(minutes=30*i)).timestamp()*1000) for i in range(19)
            if int((start + timedelta(minutes=30*i)).timestamp()*1000) not in occupied]

def run(apply=False):
    store = XanoStore('vettech', 167758)
    if store.target['tenant']:
        raise RuntimeError('Tenant inesperado; nenhuma reserva criada')
    pets = [r for r in store.pages(store.url('pet')) if r.get('nome', '').strip().casefold() == 'jessy']
    if len(pets) != 1:
        raise RuntimeError('Jessy ambigua ou ausente; informe o pet correto antes de criar registros')
    pet = pets[0]
    consents = [r for r in store.pages(store.url('acesso_autorizado'))
                if r.get('pet_id') == pet['id'] and r.get('status') == 'ativo']
    if len(consents) != 1:
        raise RuntimeError('Medico ambiguo ou sem consentimento ativo; nenhuma autorizacao sera alterada')
    vet_id = consents[0]['veterinario_id']
    previous = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else None
    if previous:
        if previous['pet_id'] != pet['id'] or previous['veterinario_id'] != vet_id:
            raise RuntimeError('Vinculo difere do manifesto existente')
        data = previous
    else:
        data = {'workspace':167758, 'pet_id':pet['id'], 'veterinario_id':vet_id,
                'first_day':datetime.now(TZ).date().isoformat(), 'operation':uuid4().hex, 'items':[]}
    if apply:
        save(data)
    rows = store.pages(store.url('consulta'))
    plan = []
    for offset in range(5):
        day = date.fromisoformat(data['first_day']) + timedelta(days=offset)
        key = 'preview-filtros:' + data['operation'] + ':' + str(offset)
        matches = [r for r in rows if r.get('operacao_chave') == key]
        recorded = next((r for r in data['items'] if r['day'] == day.isoformat()), None)
        if len(matches) > 1 or (recorded and not matches):
            raise RuntimeError('Consulta duplicada ou removida apos criacao; nao recriar automaticamente')
        if matches:
            row = matches[0]
            if row.get('pet_id') != pet['id'] or row.get('veterinario_id') != vet_id:
                raise RuntimeError('Operacao remota possui outro vinculo')
            stamp = row['agendada_para']
        else:
            free = candidates(rows, pet['id'], vet_id, day)
            if not free:
                raise RuntimeError('Nenhum horario livre; nenhuma reserva existente sera movida')
            stamp = free[0]
            if apply:
                payload = {'pet_id':pet['id'], 'veterinario_id':vet_id, 'status':'agendada',
                           'agendada_para':stamp, 'fuso':'America/Sao_Paulo', 'versao':0,
                           'motivo':'TESTE FILTROS - Jessy - ' + day.isoformat(),
                           'operacao_chave':key, 'operacao_hash':hashlib.sha256(key.encode()).hexdigest()}
                # Recheck the live consent and exact slot immediately before each write.
                if not any(r.get('pet_id') == pet['id'] and r.get('veterinario_id') == vet_id and r.get('status') == 'ativo'
                           for r in store.pages(store.url('acesso_autorizado'))):
                    raise RuntimeError('Consentimento deixou de estar ativo')
                latest = store.pages(store.url('consulta'))
                if stamp not in candidates(latest, pet['id'], vet_id, day):
                    raise RuntimeError('Horario mudou; execute novamente para escolher outro horario livre')
                result = store.request('POST', store.url('consulta'), json=payload)
                if result.status_code not in (200, 201):
                    raise RuntimeError('Criacao recusada; conferir registros pela operacao antes de repetir')
                row = result.json()
                rows.append(row)
        item = {'day':day.isoformat(), 'time':datetime.fromtimestamp(stamp/1000, TZ).strftime('%H:%M'),
                'agendada_para':stamp}
        if matches or apply:
            item['id'] = row['id']
        plan.append(item)
        if apply and not recorded:
            data['items'].append(item)
            save(data)
    if apply:
        stored = store.pages(store.url('consulta'))
        for item in data['items']:
            record = next((r for r in stored if r['id'] == item['id']), None)
            if not record or record.get('pet_id') != pet['id'] or record.get('veterinario_id') != vet_id or record.get('agendada_para') != item['agendada_para']:
                raise RuntimeError('Verificacao da reserva falhou')
        data['state'] = 'retained_for_user'
        save(data)
    print(json.dumps({'mode':'applied' if apply else 'plan', 'pet':'Jessy', 'count':len(plan),
                      'items':plan, 'manifest':str(MANIFEST.relative_to(ROOT)), 'retained':bool(apply)}, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        run(args.apply)
    except Exception as error:
        # Never expose HTTP bodies, credentials, records or tokens in failures.
        print('Populacao nao concluida: ' + str(error) if isinstance(error, RuntimeError)
              else 'Populacao nao concluida: conferir conectividade e manifesto privado', file=sys.stderr)
        raise SystemExit(1)
