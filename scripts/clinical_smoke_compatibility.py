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
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    a,c=s.data['pets']['a'],s.data['pets']['c']
    va=s.data['actors']['va']['id']
    consent=next(r for r in s.store.pages(s.store.url('acesso_autorizado')) if r['pet_id']==a and r['veterinario_id']==va)
    ids={r['id'] for r in s.store.pages(s.store.url('consulta')) if r['pet_id']==a}
    s.ok('final_redaction_revoke','PUT',f'tutor/pets/{a}/acessos/{consent["id"]}','ta',{'status':'revogado'})
    data=s.ok('redacted_agenda','GET','veterinario/agenda','va')
    s.check('redacted_fields',all(set(r)<={'id','status','agendada_para','autorizado'} for r in data['items'] if r['id'] in ids))
    s.ok('final_redaction_reactivate','PUT',f'tutor/pets/{a}/acessos/{consent["id"]}','ta',{'status':'ativo'})
    empty=s.ok('no_compatible_professional','GET',f'tutor/profissionais?pet_id={s.data["pets"]["b"]}','ta')
    s.check('compatible_search_empty_without_fabrication',empty==[])
    logs=s.ok('audit_read_immutable','GET',f'tutor/pets/{a}/auditoria','ta')
    for method in ('PUT','DELETE'):
     status,_=s.api(method,f'tutor/pets/{a}/auditoria/{logs[0]["id"]}','ta',{})
     s.check('audit_cannot_'+method.lower(),status in (400,401,403,404,405))
    disease=next(r for r in s.store.pages(s.store.url('doenca')) if r['id']==s.data['created']['doenca'][0])
    same=s.ok('reuse_normalized_disease','POST',f'veterinario/pets/{a}/doencas','va',{'payload':{'nome':'  '+disease['nome'].upper()+'  ','descricao':'Must not overwrite'}})
    s.check('normalized_catalog_reuses_id',same['id']==disease['id'])
    after=next(r for r in s.store.pages(s.store.url('doenca')) if r['id']==disease['id'])
    s.check('catalog_not_overwritten',after==disease)
    history=s.ok('other_pet_history_isolation','GET',f'tutor/pets/{c}/historico','tb')
    s.check('other_pet_no_borrowed_complements',all(not history[key] for key in ('vacinas','medicamentos','doencas','exames','diagnosticos')))

    legacy,status=s.store.write('POST','medicamento',{'nome':s.data['prefix']+'-prescrição-legada','pet_id':a,'veterinario_id':va,'dosagem':2,'tipo':'continuo','data_inicio':datetime.now(timezone.utc).date().isoformat()})
    s.check('legacy_prescription_fixture',status in (200,201))
    s.track('medicamento',legacy)
    history=s.ok('legacy_prescription_history','GET',f'tutor/pets/{a}/historico','ta')
    read=next(r for r in history['medicamentos'] if r['id']==legacy['id'])
    s.check('legacy_dose_and_unlinked_origin_preserved',read['dosagem']==2 and not read.get('consulta_id') and not read.get('dose'))
    s.discover()


if __name__ == "__main__":
    main()
