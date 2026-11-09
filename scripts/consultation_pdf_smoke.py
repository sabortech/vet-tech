"""Export contract checks against explicitly selected development fixtures.

Uses the clinical smoke ledger; prints check names only. Never prints tokens,
clinical responses or administrative credentials. Does not clean up audit logs.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from uuid import uuid4

import yaml
from clinical_smoke import Smoke, PRIVATE
from animal_catalog import save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--workspace', type=int, required=True)
    parser.add_argument('--development', action='store_true', required=True)
    parser.add_argument('--folder', type=Path, required=True)
    args = parser.parse_args()
    try:
        config = yaml.safe_load((Path.home()/'.xano/credentials.yaml').read_text())
        profile = config['profiles'][args.profile]
        if int(profile['workspace']) != args.workspace:
            raise RuntimeError('Workspace mismatch')
        smoke = Smoke(args.folder, profile_name=args.profile, workspace=args.workspace, profile_config=profile)
        ready = (not smoke.data.get("cleaned") and all(smoke.data.get("actors",{}).get(a,{}).get("token") for a in ("ta","tb","va","vb")) and all(k in smoke.data.get("pets",{}) for k in ("a","b","c")))
        if not ready:
            smoke.setup()
        # The ledger may outlive token TTL; authenticate only its synthetic accounts.
        prefix=smoke.data.get('prefix','')
        if not prefix.startswith('qa-clinical-'):
            raise RuntimeError('Expected synthetic clinical ledger')
        for actor in ('ta','tb','va','vb'):
            user=smoke.data['actors'][actor]
            if prefix not in user['email']:
                raise RuntimeError('Non-synthetic account refused')
            code,login=smoke.api('POST','acesso/login',payload={'email':user['email'],'password':user['password']},group='H62nB-j2')
            smoke.check('refresh_pdf_fixture_session_'+actor,code==200 and bool(login.get('authToken')))
            user['token']=login['authToken'];smoke.persist()
        pet = smoke.data['pets']['a'];other = smoke.data['pets']['c']
        veterinarian = smoke.data['actors']['va']['id']
        def fixture(name, status, target=pet):
            if name in smoke.data.get('pdf_consultations', {}):
                return smoke.data['pdf_consultations'][name]
            row, code = smoke.store.write('POST', 'consulta', {'pet_id':target,'veterinario_id':veterinarian,
                'status':status,'data_atendimento':'2026-11-04','motivo':'Teste sintético PDF',
                'diagnostico':'Registro sintético — acentuação ç ã é','obs':'Sem dados reais',
                'rascunho':{'obs':'RASCUNHO_NAO_EXPORTAR'}})
            smoke.check('create_pdf_fixture_'+name,code in (200,201) and isinstance(row,dict) and bool(row.get('id')))
            value=smoke.track('consulta',row)
            smoke.data.setdefault('pdf_consultations',{})[name]=value;smoke.persist()
            return value
        consents=smoke.ok('pdf_fixture_access','GET',f'tutor/pets/{pet}/acessos','ta')
        permit=next((r for r in consents if r.get('veterinario_id')==veterinarian),None)
        if permit is None:
            permit,code=smoke.store.write('POST','acesso_autorizado',{'pet_id':pet,'veterinario_id':veterinarian,'status':'ativo'})
            smoke.check('create_pdf_fixture_consent',code in (200,201) and bool(permit.get('id')))
            smoke.track('acesso_autorizado',permit)
        if permit.get('status')!='ativo':
            smoke.ok('pdf_fixture_reactivate','PUT',f'tutor/pets/{pet}/acessos/{permit['id']}','ta',{'status':'ativo'})
        complete=fixture('finalizada','finalizada')
        second=fixture('segunda','finalizada')
        foreign=fixture('alheia','finalizada',other)
        # Exercise all categories and the SQL join with ledgered, synthetic records.
        def complement(key,table,data):
            value=smoke.data.setdefault('pdf_complements',{}).get(key)
            if value:return value
            row,code=smoke.store.write('POST',table,data)
            smoke.check('create_pdf_complement_'+key,code in (200,201) and isinstance(row,dict) and bool(row.get('id')))
            value=smoke.track(table,row)
            smoke.data['pdf_complements'][key]=value;smoke.persist();return value
        disease_name=prefix+'-diagnostico-pdf'
        disease=complement('disease','doenca',{'nome':disease_name,'nome_normalizado':disease_name,'descricao':'Catálogo sintético PDF'})
        common={'pet_id':pet,'consulta_id':complete,'veterinario_id':veterinarian}
        complement('diagnosis','consulta_doenca',{**common,'doenca_id':disease,'origem_linha':'pdf-diagnosis','data_diagnostico':'2026-11-04','estado':'ativa','observacoes':'Diagnóstico pontual sintético'})
        complement('vaccine','vacina',{**common,'origem_linha':'pdf-vaccine','vacina':'Vacina sintética PDF','lote':'QA','data_aplicacao':'2026-11-04'})
        complement('medication','medicamento',{**common,'origem_linha':'pdf-medication','nome':'Medicamento sintético PDF','dose':1,'unidade':'mg','frequencia':'Diária','via':'Oral','tipo':'outro','data_inicio':'2026-11-04'})
        complement('exam','exame',{**common,'origem_linha':'pdf-exam','tipo':'Exame sintético PDF','status':'realizado','data_solicitacao':'2026-11-04','data_realizacao':'2026-11-04','resultado':'Resultado sintético PDF'})
        def route(c=complete,p=pet):return f'tutor/pets/{p}/consultas/{c}/exportar'
        def post(c=complete,p=pet,actor='ta',operation=None):
            return smoke.api('POST',route(c,p),actor,{'operacao':operation or str(uuid4())})
        code,body=post()
        smoke.check('export_finalized_owned',code==200 and body.get('consulta',{}).get('id')==complete and bool(body.get('auditoria_id')))
        authorized_document = body
        smoke.check('all_complement_categories',all(len(body.get(k,[]))>=1 for k in ('vacinas','medicamentos','diagnosticos','exames')))
        smoke.check('joined_diagnosis_name',any(r.get('nome')==disease_name for r in body['diagnosticos']))
        smoke.check('no_draft_or_consolidated', 'rascunho' not in body['consulta'] and 'doencas' not in body)
        for name,c,p,actor in [('foreign_tutor',complete,pet,'tb'),('wrong_pet',foreign,pet,'ta'),
                ('foreign_pet',foreign,other,'ta'),('wrong_profile',complete,pet,'va'),
                ('missing_id',2147483640,pet,'ta'),('anonymous',complete,pet,None)]:
            code,body=post(c,p,actor)
            smoke.check('deny_'+name, code in (400,401,403,404) and 'consulta' not in body and 'auditoria_id' not in body)
        for status in ['agendada','em_atendimento','cancelada',None]:
            c=fixture(str(status),status);code,body=post(c)
            smoke.check('deny_status_'+str(status),code in (400,409) and 'consulta' not in body)
        operation=str(uuid4());first=post(operation=operation);again=post(operation=operation)
        smoke.check('retry_same_audit',first[0]==again[0]==200 and first[1]['auditoria_id']==again[1]['auditoria_id'])
        code,body=post(second,operation=operation)
        smoke.check('deny_reused_key_for_other_consultation',code in (400,409) and 'consulta' not in body)
        concurrent=str(uuid4())
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies=list(pool.map(lambda _:post(operation=concurrent),range(2)))
        # A race losing the DB unique constraint must fail closed; retry recovers the same audit.
        smoke.check('concurrent_failures_have_no_data',all(code==200 or 'consulta' not in body for code,body in replies))
        retry=post(operation=concurrent)
        smoke.check('concurrent_retry_succeeds',retry[0]==200)
        logs=smoke.ok('read_pdf_audit','GET',f'tutor/pets/{pet}/auditoria','ta')
        ids=[r['id'] for r in logs if r.get('acao')=='exportar_consulta' and r.get('consulta_id')==complete]
        smoke.check('idempotency_one_log',ids.count(retry[1]['auditoria_id'])==1)
        smoke.check('audit_actor_and_target',all(r.get('tutor_id')==smoke.data['actors']['ta']['id'] and r.get('veterinario_id')==veterinarian for r in logs if r['id'] in ids))
        # Shared preview and professional export; same clinical recorte, separate audit actions.
        for actor, prefix in [('ta','tutor'),('va','veterinario')]:
            preview_route=f'{prefix}/pets/{pet}/consultas/{complete}/previa-pdf'
            code,preview=smoke.api('GET',preview_route,actor)
            smoke.check('preview_'+prefix,code==200 and preview.get('consulta',{}).get('id')==complete and bool(preview.get('auditoria_id')))
            code,again_preview=smoke.api('GET',preview_route,actor)
            smoke.check('preview_audited_each_open_'+prefix,code==200 and again_preview['auditoria_id']!=preview['auditoria_id'])
            code,download=smoke.api('POST',f'{prefix}/pets/{pet}/consultas/{complete}/exportar',actor,{'operacao':str(uuid4())})
            smoke.check('preview_matches_export_'+prefix,code==200 and all(preview[k]==download[k] for k in ('pet','consulta','vacinas','medicamentos','diagnosticos','exames')))
        shared=str(uuid4())
        t=post(operation=shared)
        vr=f'veterinario/pets/{pet}/consultas/{complete}/exportar'
        v=smoke.api('POST',vr,'va',{'operacao':shared})
        smoke.check('actor_profile_operation_namespace',t[0]==v[0]==200 and t[1]['auditoria_id']!=v[1]['auditoria_id'])
        v2=smoke.api('POST',vr,'va',{'operacao':shared})
        smoke.check('vet_retry_same_audit',v2[0]==200 and v2[1]['auditoria_id']==v[1]['auditoria_id'])
        for status in ['agendada','em_atendimento','cancelada',None]:
            c=fixture(str(status),status)
            for prefix,actor in [('tutor','ta'),('veterinario','va')]:
                code,body=smoke.api('GET',f'{prefix}/pets/{pet}/consultas/{c}/previa-pdf',actor)
                smoke.check('preview_deny_'+prefix+'_'+str(status),code in (400,404,409) and 'consulta' not in body)
        for prefix,actor in [('tutor','tb'),('veterinario','vb')]:
            code,body=smoke.api('GET',f'{prefix}/pets/{pet}/consultas/{complete}/previa-pdf',actor)
            smoke.check('preview_deny_other_actor_'+prefix,code in (401,403,404) and 'consulta' not in body)
        consent=next(r for r in smoke.ok('pdf_consents','GET',f'tutor/pets/{pet}/acessos','ta') if r.get('veterinario_id')==veterinarian)
        smoke.ok('pdf_activate_consent','PUT',f'tutor/pets/{pet}/acessos/{consent["id"]}','ta',{'status':'ativo'})
        try:
            smoke.ok('pdf_revoke_consent','PUT',f'tutor/pets/{pet}/acessos/{consent["id"]}','ta',{'status':'revogado'})
            for method,route,body in [('GET',f'veterinario/pets/{pet}/consultas/{complete}/previa-pdf',None),('POST',vr,{'operacao':shared})]:
                code,body=smoke.api(method,route,'va',body)
                smoke.check('pdf_revoked_'+method,code in (403,404) and 'consulta' not in body)
        finally:
            smoke.ok('pdf_restore_consent','PUT',f'tutor/pets/{pet}/acessos/{consent["id"]}','ta',{'status':'ativo'})
        # The debugger returns HTTP 200 for execution exceptions, so inspect result.status.
        records=smoke.store.pages(smoke.store.url('log_acesso'))
        existing=next(r for r in records if r['id']==retry[1]['auditoria_id'])
        fault=smoke.store.request('POST',smoke.store.base+'/function/run',json={
            'name':'Clinical/audit','input':{k:existing[k] for k in
                ['pet_id','veterinario_id','tutor_id','consulta_id','acao','operacao']}})
        result=fault.json().get('result',{}) if fault.is_success else {}
        smoke.check('audit_write_failure_is_exception',result.get('status')=='exception')
        after=smoke.store.pages(smoke.store.url('log_acesso'))
        smoke.check('audit_failure_preserves_original',next(r for r in after if r['id']==existing['id'])==existing)
        smoke.check('audit_failure_does_not_insert',sum(r.get('operacao')==existing['operacao'] for r in after)==1)
        denied,_=smoke.api('DELETE',f'tutor/pets/{pet}/auditoria/{existing["id"]}','ta')
        smoke.check('audit_has_no_user_delete',denied in (401,403,404,405))
        # Confirm remote data maps and renders without persisting a public PDF.
        import sys
        from io import BytesIO
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from pypdf import PdfReader
        from vet_tech.features.clinical.consultation_pdf import map_consultation_document
        from vet_tech.features.clinical.consultation_pdf_template import render_consultation_pdf
        pdf=render_consultation_pdf(map_consultation_document(authorized_document,pet,complete))
        text=''.join(p.extract_text() for p in PdfReader(BytesIO(pdf)).pages)
        smoke.check('remote_data_pdf_matches',pdf.startswith(b'%PDF-') and authorized_document['pet']['nome'] in text and 'Teste sintético PDF' in text)
        smoke.check('remote_pdf_has_confirmed_audit',any(r['id']==authorized_document['auditoria_id'] and r['consulta_id']==complete for r in after))
        smoke.discover()
        save(args.folder/'pdf-result.json',{'checks':smoke.data['checks'],'endpoint':'tutor/pets/{pet_id}/consultas/{consulta_id}/exportar','mode':'development-synthetic'})
        print(json.dumps({'export_checks':'passed','private_ledger':str(smoke.path.relative_to(PRIVATE.parent.parent))}))
    except Exception:
        # Do not emit exception reprs: transport errors can contain headers or response data.
        print('Verificação PDF incompleta; consultar o ledger privado e os nomes dos checks. Nenhuma credencial foi exibida.')
        return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
