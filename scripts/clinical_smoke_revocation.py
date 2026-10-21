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
    s=Smoke(PRIVATE/args.run)
    a=s.data['pets']['a']
    r=s.ok('revocation_race_booking','POST','tutor/consultas','ta',{'payload':s.booking(hour='13:00',offset=6)})
    cid=s.track('consulta',r)
    s.ok('revocation_race_start','POST',f'veterinario/consultas/{cid}/iniciar','va')
    row=s.ok('revocation_race_draft','GET',f'veterinario/consultas/{cid}/rascunho','va')['consulta']
    consent=next(r for r in s.store.pages(s.store.url('acesso_autorizado')) if r['pet_id']==a and r['veterinario_id']==s.data['actors']['va']['id'])
    record={'motivo':'QA concorrência','diagnostico':'Registro sintético de concorrência','data_atendimento':datetime.now(timezone.utc).date().isoformat()}
    calls=[('PUT',f'tutor/pets/{a}/acessos/{consent["id"]}','ta',{'status':'revogado'}),('POST',f'veterinario/consultas/{cid}/finalizar','va',{'versao':row['versao'],'payload':record})]
    with ThreadPoolExecutor(max_workers=2) as pool:
     results=list(pool.map(lambda args:s.api(*args),calls))
    s.check('concurrent_revocation_success',results[0][0]==200)
    s.check('concurrent_finalize_authorized_or_denied',results[1][0] in (200,403))
    logs=s.store.pages(s.store.url('log_acesso'))
    revoked=max(r['id'] for r in logs if r.get('pet_id')==a and r.get('acao')=='revogado')
    finals=[r for r in logs if r.get('consulta_id')==cid and r.get('acao')=='finalizar']
    s.check('no_publication_after_committed_revocation',not finals or finals[0]['id']<revoked)
    s.deny('post_race_access_denied','GET',f'veterinario/consultas/{cid}/rascunho','va')
    s.ok('post_race_reactivate','PUT',f'tutor/pets/{a}/acessos/{consent["id"]}','ta',{'status':'ativo'})
    s.discover()


if __name__ == "__main__":
    main()
