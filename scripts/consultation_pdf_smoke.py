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
        complete=fixture('finalizada','finalizada')
        second=fixture('segunda','finalizada')
        foreign=fixture('alheia','finalizada',other)
        def route(c=complete,p=pet):return f'tutor/pets/{p}/consultas/{c}/exportar'
        def post(c=complete,p=pet,actor='ta',operation=None):
            return smoke.api('POST',route(c,p),actor,{'operacao':operation or str(uuid4())})
        code,body=post()
        smoke.check('export_finalized_owned',code==200 and body.get('consulta',{}).get('id')==complete and bool(body.get('auditoria_id')))
        authorized_document = body
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
