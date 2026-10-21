"""Explicit synthetic-fixture verification; read deployment-review.md before use.
Tokens, records and screenshots remain in the private run directory.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    import sys
    from datetime import datetime,timezone,timedelta
    from concurrent.futures import ThreadPoolExecutor
    from clinical_smoke import Smoke,PRIVATE
    s=Smoke(PRIVATE/args.run)
    a=s.data['pets']['a']
    def start(name,hour):
     r=s.ok(name,'POST','tutor/consultas','ta',{'payload':s.booking(hour=hour,offset=6)})
     cid=s.track('consulta',r)
     s.ok(name+'_start','POST',f'veterinario/consultas/{cid}/iniciar','va')
     row=s.ok(name+'_draft','GET',f'veterinario/consultas/{cid}/rascunho','va')['consulta']
     return cid,row['versao']
    cid,version=start('audit_failure_fixture','11:00')
    record={'motivo':'QA sintético','diagnostico':'Registro sintético sem efeitos reais','data_atendimento':datetime.now(timezone.utc).date().isoformat()}
    fake,status=s.store.write('POST','log_acesso',{'pet_id':a,'veterinario_id':s.data['actors']['va']['id'],'consulta_id':cid,'acao':'qa_conflict_fixture','ocorrido_em':int(datetime.now(timezone.utc).timestamp()*1000),'operacao':f'finalizar:{cid}'})
    s.check('audit_failure_fixture_created',status in (200,201))
    fid=s.track('log_acesso',fake)
    status,_=s.api('POST',f'veterinario/consultas/{cid}/finalizar','va',{'versao':version,'payload':record})
    s.check('audit_failure_blocks_publication',status>=400)
    row=s.ok('audit_failure_rollback_read','GET',f'veterinario/consultas/{cid}/rascunho','va')['consulta']
    s.check('audit_failure_rolls_back_status',row['status']=='em_atendimento' and row['versao']==version)
    s.store.request('DELETE',s.store.url('log_acesso')+f'/{fid}')
    with ThreadPoolExecutor(max_workers=2) as pool:
     results=list(pool.map(lambda _:s.api('POST',f'veterinario/consultas/{cid}/finalizar','va',{'versao':version,'payload':record}),range(2)))
    s.check('concurrent_finalization_same_result',all(status==200 for status,_ in results) and results[0][1]==results[1][1])
    logs=s.store.pages(s.store.url('log_acesso'))
    s.check('single_finalization_audit',len([r for r in logs if r.get('consulta_id')==cid and r.get('acao')=='finalizar'])==1)

    cid,version=start('retroactive_evolution_fixture','12:00')
    disease=s.data['created']['doenca'][0]
    older=(datetime.now(timezone.utc)-timedelta(days=1)).date().isoformat()
    record['doencas']=[{'linha_id':'qa-old','doenca_id':disease,'data_diagnostico':older,'estado':'ativa','observacoes':'Registro retroativo QA'}]
    s.ok('publish_older_evolution','POST',f'veterinario/consultas/{cid}/finalizar','va',{'versao':version,'payload':record})
    history=s.ok('evolution_history','GET',f'tutor/pets/{a}/historico','ta')
    s.check('older_publication_does_not_regress_condition',next(r for r in history['doencas'] if r.get('doenca_id')==disease)['estado']=='controlada')
    s.check('both_evolutions_preserved',len([r for r in history['diagnosticos'] if r['doenca_id']==disease])==2)
    s.discover()
    print({'deep_checks':'passed'},flush=True)


if __name__ == "__main__":
    main()
