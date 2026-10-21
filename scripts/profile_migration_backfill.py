"""Backfill technical email reservations and the versioned specialty catalog.

Default is dry-run. Apply only after publishing the write-frozen migration
bundle. Never changes a domain identity, password hash, clinic or pet.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_migration_inventory import ROOT, PRIVATE_ROOT, cli_profile, digest, migration_plan, read_pages


def freeze_bundle():
    target = ROOT / '.venv/shared-profile-migration-frozen'
    shutil.copytree(ROOT / 'xano', target, dirs_exist_ok=True)
    helper = target / 'function/identity/check_email_available.xs'
    source = helper.read_text(encoding='utf-8')
    source = source.replace('  stack {', '  stack {\n    precondition (false) {\n      error_type = "accessdenied"\n      error = "Cadastros temporariamente suspensos para atualização. Tente novamente em breve."\n    }', 1)
    helper.write_text(source, encoding='utf-8')
    print('Write-frozen bundle prepared under .venv/shared-profile-migration-frozen. No network write.')


def backfill(snapshot_path, apply=False):
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
    plan = migration_plan(snapshot['records'])
    if not plan['ready_for_backfill']:
        raise RuntimeError('Snapshot contains conflicts; backfill refused')
    profile = cli_profile()
    if snapshot['workspace'] != profile['workspace']:
        raise RuntimeError('Snapshot workspace differs from the configured workspace')
    origin = profile['instance_origin'].rstrip('/')
    base = origin + '/api:meta/workspace/' + str(profile['workspace'])
    manifest = {'captured_at':datetime.now(timezone.utc).isoformat(), 'workspace':profile['workspace'],
                'mode':'apply' if apply else 'dry-run', 'created':[], 'counts':{}}
    folder = PRIVATE_ROOT / ('backfill-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    folder.mkdir(parents=True)
    path = folder / 'manifest.json'
    def save():
        path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    with httpx.Client(timeout=40, headers={'Authorization':'Bearer '+profile['access_token']}) as client:
        tables = {row['name']:row['id'] for row in read_pages(client, base+'/table')}
        if not {'reserva_email','especialidade'} <= tables.keys():
            raise RuntimeError('Publish the additive schemas before backfill')
        for name, rows in snapshot['records'].items():
            current = read_pages(client, f'{base}/table/{tables[name]}/content')
            if {str(r['id']):digest(r) for r in current} != plan['record_digests'][name]:
                raise RuntimeError('Domain records differ from the private snapshot; repeat inventory under the write freeze')
        if apply:
            functions = read_pages(client, base+'/function')
            helper = next((row for row in functions if row['name'] == 'Identity/check_email_available'), None)
            if helper is None:
                raise RuntimeError('Migration helper is not published')
            published = client.get(base+'/function/'+str(helper['id']), params={'include_xanoscript':'true', 'include_draft':'false'})
            if not published.is_success:
                raise RuntimeError('Unable to verify the published write freeze')
            script = published.json().get('xanoscript', {})
            source = script.get('value','') if isinstance(script,dict) else str(script)
            if 'precondition (false)' not in source:
                raise RuntimeError('Published registration helper is not write-frozen; apply refused')
        for name, desired in [('reserva_email',plan['reservations_to_create']),
                              ('especialidade',json.loads((ROOT/'xano/seed/especialidades.json').read_text(encoding='utf-8')))]:
            current = read_pages(client, f'{base}/table/{tables[name]}/content')
            key = 'email' if name == 'reserva_email' else 'chave'
            mapping = {}
            for row in current:
                if row[key] in mapping:
                    raise RuntimeError('Duplicate technical key; backfill refused')
                mapping[row[key]] = row
            missing = []
            for row in desired:
                previous = mapping.get(row[key])
                if previous is not None:
                    if any(previous.get(field) != value for field,value in row.items()):
                        raise RuntimeError('Existing reservation/catalog differs from the migration plan')
                    continue
                missing.append(row)
            manifest['counts'][name] = {'existing':len(current), 'to_create':len(missing)}
            save()
            if apply:
                for row in missing:
                    response = client.post(f'{base}/table/{tables[name]}/content', json=row)
                    if not response.is_success:
                        raise RuntimeError('Backfill write failed; keep the write freeze and inspect the private manifest')
                    manifest['created'].append({'table':name,'id':response.json()['id']})
                    save()
        # Verify domain records remained byte-for-byte equivalent as JSON.
        for name in snapshot['records']:
            current = read_pages(client, f'{base}/table/{tables[name]}/content')
            if {str(r['id']):digest(r) for r in current} != plan['record_digests'][name]:
                raise RuntimeError('Domain digest comparison failed; keep the write freeze')
    manifest['domain_records_preserved'] = True
    save()
    print(json.dumps({'mode':manifest['mode'],'counts':manifest['counts'], 'created_count':len(manifest['created']),
                      'domain_records_preserved':True,'private_manifest':str(path.relative_to(ROOT))}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-freeze',action='store_true')
    parser.add_argument('--snapshot',type=Path)
    parser.add_argument('--apply',action='store_true')
    args = parser.parse_args()
    try:
        if args.prepare_freeze:
            freeze_bundle()
        if args.snapshot:
            backfill(args.snapshot, args.apply)
        elif args.apply:
            raise RuntimeError('Snapshot required')
        return 0
    except (RuntimeError, ValueError, KeyError, OSError, httpx.HTTPError):
        print('Backfill not completed. Keep registrations suspended and inspect the private snapshot/manifest. No domain row is modified by this tool.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
