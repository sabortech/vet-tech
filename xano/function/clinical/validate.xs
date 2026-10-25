// Pure normalization/validation in Xano's native Lambda runtime. No network IO.
function "Clinical/validate" {
  input {
    text kind
    json payload
    timestamp current_time
  }
  stack {
    api.lambda {
      code = """
        const p = $input.payload;
        const kind = $input.kind;
        const now = Number($input.current_time);
        const today = new Intl.DateTimeFormat('en-CA', {timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(now));
        const fail = message => { throw new Error(message); };
        const text = (v, name, required=true, max=4000) => {
          if (typeof v !== 'string' || (required && !v.trim()) || v.length > max) fail('Preencha corretamente: '+name+'.');
          return v.trim();
        };
        const date = (v, name, required=true) => {
          if (!v && !required) return null;
          if (typeof v !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(v)) fail('Data inválida: '+name+'.');
          const d = new Date(v+'T12:00:00Z');
          if (!Number.isFinite(d.getTime()) || d.toISOString().slice(0,10)!==v) fail('Data inválida: '+name+'.');
          return v;
        };
        const integer = (v,name) => { const n=Number(v); if (!Number.isSafeInteger(n)||n<=0) fail('Identificador inválido: '+name+'.'); return n; };
        try {
          if (!p || typeof p!=='object' || Array.isArray(p)) fail('Formato inválido.');
          if (kind==='booking') {
            const day=date(p.dia,'dia'), hour=text(p.horario,'horário',true,5);
            if (!/^\d{2}:\d{2}$/.test(hour) || hour<'08:00' || hour>'17:00' || Number(hour.slice(3))>59) fail('Escolha um horário entre 08h e 17h.');
            const instant=Date.parse(day+'T'+hour+':00-03:00');
            if (!Number.isFinite(instant)) fail('Data inválida.');
            const key=text(p.operacao,'operação',true,100);
            if (!/^[a-zA-Z0-9-]{16,100}$/.test(key)) fail('Operação inválida.');
            const clean={pet_id:integer(p.pet_id,'pet'),veterinario_id:integer(p.veterinario_id,'profissional'),
              motivo:text(p.motivo,'motivo',true,1000),agendada_para:instant,fuso:'America/Sao_Paulo',operacao:key};
            return {valid:true,value:clean,future:instant>now,signature:JSON.stringify(clean)};
          }
          if (kind==='disease') {
            const name=text(p.nome,'nome da doença',true,160).normalize('NFC').replace(/\s+/g,' ');
            return {valid:true,value:{nome:name,nome_normalizado:name.toLocaleLowerCase('pt-BR'),descricao:text(p.descricao||'','descrição',false)}};
          }
          const complete = kind==='finalize';
          if (!['draft','finalize'].includes(kind)) fail('Operação inválida.');
          for (const key of ['id','pet_id','veterinario_id','tutor_id','consulta_id','status']) {
            if (Object.hasOwn(p,key)) fail('Identidade e estado da consulta não podem ser alterados.');
          }
          const clean={motivo:text(p.motivo||'','motivo',complete,1000),diagnostico:text(p.diagnostico||'','diagnóstico',complete),
            obs:text(p.obs||'','observações',false),data_atendimento:date(p.data_atendimento,'atendimento',complete),
            retorno_previsto:date(p.retorno_previsto,'retorno',false)};
          if (clean.data_atendimento>today) fail('Atendimento realizado não pode ter data futura.');
          if (clean.retorno_previsto && clean.data_atendimento && clean.retorno_previsto<clean.data_atendimento) fail('Retorno anterior ao atendimento.');
          for (const group of ['vacinas','medicamentos','doencas','exames']) {
            const rows=p[group]||[];
            if (!Array.isArray(rows)||rows.length>100) fail('Lista inválida: '+group+'.');
            const seen=new Set();
            clean[group]=rows.map((row,index)=>{ try {
              if (!row || typeof row!=='object' || Array.isArray(row)) fail('Linha inválida: '+group+'.');
              for (const key of ['id','pet_id','veterinario_id','tutor_id','consulta_id']) {
                if (Object.hasOwn(row,key)) fail('Vínculo de registro não pode ser alterado.');
              }
              const id=text(row.linha_id,'linha',true,100);
              if (!/^[a-zA-Z0-9-]{1,100}$/.test(id)||seen.has(id)) fail('Identificação repetida de linha.');
              seen.add(id);
              // Drafts keep editable values but never accept foreign pet/author/row IDs.
              const fields={vacinas:['vacina','data_aplicacao','lote','data_prox_dose'],medicamentos:['nome','dose','unidade','frequencia','via','tipo','data_inicio','data_fim'],doencas:['doenca_id','data_diagnostico','estado','observacoes'],exames:['tipo','status','data_solicitacao','data_realizacao','resultado']}[group];
              const c={linha_id:id};
              for (const field of fields) { const v=row[field]; if (v!=null && !['string','number'].includes(typeof v)) fail('Campo inválido.'); c[field]=v==null?'':v; }
              if (!complete) return c;
              if (group==='vacinas') {
                c.vacina=text(c.vacina,'vacina'); c.lote=text(c.lote,'lote');
                c.data_aplicacao=date(c.data_aplicacao,'aplicação'); c.data_prox_dose=date(c.data_prox_dose,'próxima dose',false);
                if (c.data_aplicacao>today || (c.data_prox_dose && c.data_prox_dose<c.data_aplicacao)) fail('Datas inconsistentes da vacina.');
              } else if (group==='medicamentos') {
                for (const f of ['nome','unidade','frequencia','via']) c[f]=text(c[f],f);
                c.dose=Number(c.dose); if (!Number.isFinite(c.dose)||c.dose<=0) fail('Dose inválida.');
                if (!['continuo','vermifugo','antipulgas','outro'].includes(c.tipo)) fail('Tipo de medicamento inválido.');
                c.data_inicio=date(c.data_inicio,'início'); c.data_fim=date(c.data_fim,'fim',c.tipo!=='continuo');
                if (c.data_fim && c.data_fim<c.data_inicio) fail('Fim anterior ao início.');
              } else if (group==='doencas') {
                c.doenca_id=integer(c.doenca_id,'doença'); c.data_diagnostico=date(c.data_diagnostico,'diagnóstico');
                if (c.data_diagnostico>today || !['ativa','em_tratamento','curada','controlada'].includes(c.estado)) fail('Evolução de doença inválida.');
                c.observacoes=text(c.observacoes,'observações',false);
              }
          else {
                c.tipo=text(c.tipo,'tipo de exame'); c.data_solicitacao=date(c.data_solicitacao,'solicitação');
                if (!['solicitado','realizado'].includes(c.status)) fail('Estado do exame inválido.');
                c.data_realizacao=date(c.data_realizacao,'realização',c.status==='realizado');
                c.resultado=text(c.resultado,'resultado',c.status==='realizado');
                if (c.data_solicitacao>today || c.data_realizacao>today || (c.data_realizacao && c.data_realizacao<c.data_solicitacao)) fail('Datas de exame inconsistentes.');
                if (c.status==='solicitado' && (c.data_realizacao||c.resultado)) fail('Resultado exige exame realizado.');
              }
              return c;
              } catch(error) { fail(group+', linha '+(index+1)+': '+error.message); }
            });
          }
          return {valid:true,value:clean};
        } catch (error) { return {valid:false,error:error.message}; }
      """
      timeout = 5
    } as $validation
    precondition ($validation.valid) {
      error_type = "inputerror"
      error = $validation.error
    }
  }
  response = $validation
  tags = ["vettech", "clinical"]
  guid = "ooE1t1Vq7KbkYw635_k01MEIQkg"
}
