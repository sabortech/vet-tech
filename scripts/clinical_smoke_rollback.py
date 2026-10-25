"""Explicit synthetic-fixture verification; read deployment-review.md before use.
Tokens, records and screenshots remain in the private run directory.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    import sys
    from datetime import datetime,timezone
    from concurrent.futures import ThreadPoolExecutor
    from clinical_smoke import Smoke,PRIVATE
    from profile_migration_inventory import digest
    s=Smoke(PRIVATE/args.run)
    owned=set(s.data['pets'].values())
    consult=next(r for r in s.store.pages(s.store.url('consulta')) if r['pet_id'] in owned and r['status']=='em_atendimento')
    cid=consult['id']
    record={'motivo':'QA rollback','diagnostico':'Rascunho sintético concorrente','data_atendimento':datetime.now(timezone.utc).date().isoformat()}
    with ThreadPoolExecutor(max_workers=2) as pool:
     results=list(pool.map(lambda _:s.api('PUT',f'veterinario/consultas/{cid}/rascunho','va',{'versao':consult['versao'],'payload':record}),range(2)))
    s.check('concurrent_draft_one_version_winner',sorted(status for status,_ in results)==[200,400])
    before={table:[r for r in s.store.pages(s.store.url(table)) if r.get('consulta_id')==cid] for table in ('vacina','medicamento','exame','consulta_doenca')}
    row=next(r for r in s.store.pages(s.store.url('consulta')) if r['id']==cid)
    today=record['data_atendimento']
    record['vacinas']=[{'linha_id':'qa-db-rollback','vacina':'Registro sintético de rollback','lote':'QA','data_aplicacao':today}]
    record['doencas']=[{'linha_id':'qa-invalid','doenca_id':2147483647,'data_diagnostico':today,'estado':'ativa'}]
    s.deny('rollback_after_actual_complement_insert','POST',f'veterinario/consultas/{cid}/finalizar','va',{'versao':row['versao'],'payload':record})
    after={table:[r for r in s.store.pages(s.store.url(table)) if r.get('consulta_id')==cid] for table in before}
    s.check('database_complements_unchanged_after_rollback',digest(before)==digest(after))
    current=next(r for r in s.store.pages(s.store.url('consulta')) if r['id']==cid)
    s.check('database_draft_and_consultation_unchanged_after_rollback',digest(row)==digest(current))
    s.discover()


if __name__ == "__main__":
    main()
