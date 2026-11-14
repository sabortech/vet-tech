function "Direct/operate" {
  input {
    text profile
    int actor_id
    json payload
  }
  stack {
    api.lambda {
      code = """
        const p=$input.payload,profile=$input.profile;
        const uuid=v=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(v);
        if(!['tutor','veterinario'].includes(profile)||!Number.isInteger($input.actor_id)||$input.actor_id<1)throw Error('Sessão inválida.');
        if(!p||!['veterinarians','tutors','list','start','get','send','edit','delete'].includes(p.action))throw Error('Operação inválida.');
        if((p.action==='tutors'&&profile!=='veterinario')||(p.action==='veterinarians'&&profile!=='tutor'))throw Error('Conversa não disponível.');
        const page=p.page??1,search=p.search??'';
        if(!Number.isInteger(page)||page<1||page>10000||typeof search!=='string'||search.length>100)throw Error('Busca inválida.');
        const peer=profile==='tutor'?p.veterinario_id:p.tutor_id;
        if(p.action==='start'&&(!Number.isInteger(peer)||peer<1))throw Error('Contato não disponível.');
        if(['get','send','edit','delete'].includes(p.action)&&(!Number.isInteger(p.thread_id)||p.thread_id<1))throw Error('Conversa não disponível.');
        if(['send','edit','delete'].includes(p.action)&&!uuid(p.operation_id))throw Error('Operação inválida.');
        if(['send','edit'].includes(p.action)&&(typeof p.message!=='string'||!p.message.trim()||p.message.length>1000))throw Error('Mensagem inválida.');
        if(['edit','delete'].includes(p.action)&&(!uuid(p.message_id)||!Number.isInteger(p.expected_revision)||p.expected_revision<0))throw Error('Mensagem inválida.');
        if(p.read_through!==undefined&&(!['get','send'].includes(p.action)||!uuid(p.read_through)))throw Error('Confirmação de leitura inválida.');
        if(p.read_revision!==undefined&&(!Number.isInteger(p.read_revision)||p.read_revision<0))throw Error('Confirmação de leitura inválida.');
        return {...p,tutor_id:profile==='tutor'?$input.actor_id:p.tutor_id,veterinario_id:profile==='veterinario'?$input.actor_id:p.veterinario_id,page,search:search.trim(),search_id:/^[0-9]+$/.test(search.trim())?Number(search):0,...(['send','edit'].includes(p.action)?{message:p.message.trim()}:{})};
        """
    } as $p
    var $reply { value = null }
    conditional {
      if ($p.action == "tutors") {
        db.query tutor {
          where = $p.search == "" || $db.tutor.nome includes $p.search || $db.tutor.id == $p.search_id
          sort = {tutor.nome: "asc", tutor.id: "asc"}

                  return = {type: "list", paging: {page: $p.page, per_page: 20, metadata: true}}

                  output = ["items.id", "items.nome", "nextPage", "curPage"]
        } as $rows
        api.lambda {
          code = """
            const rows=$var.rows;
            return {tutors:(Array.isArray(rows)?rows:rows.items||[]).map(r=>({id:r.id,name:r.nome||''})),page:$var.p.page,has_next:!Array.isArray(rows)&&rows.nextPage!=null};
            """
        } as $reply
      }
      elseif ($p.action == "veterinarians") {
        db.query veterinario {
          where = $p.search == "" || $db.veterinario.nome includes $p.search || $db.veterinario.id == $p.search_id
          sort = {veterinario.nome: "asc", veterinario.id: "asc"}

                  return = {type: "list", paging: {page: $p.page, per_page: 20, metadata: true}}

                  output = ["items.id", "items.nome", "nextPage", "curPage"]
        } as $rows
        api.lambda {
          code = """
            const rows=$var.rows;
            return {veterinarians:(Array.isArray(rows)?rows:rows.items||[]).map(r=>({id:r.id,name:r.nome||''})),page:$var.p.page,has_next:!Array.isArray(rows)&&rows.nextPage!=null};
            """
        } as $reply
      }
      elseif ($p.action == "list") {
        db.query direct_conversation {
          join = {
            tutor: {table: "tutor", type: "left", where: $db.direct_conversation.tutor_id == $db.tutor.id}
            veterinario: {table: "veterinario", type: "left", where: $db.direct_conversation.veterinario_id == $db.veterinario.id}
          }
          eval = {tutor_name: $db.tutor.nome, veterinarian_name: $db.veterinario.nome}
          where = ($input.profile == "tutor" && $db.direct_conversation.tutor_id == $input.actor_id) || ($input.profile == "veterinario" && $db.direct_conversation.veterinario_id == $input.actor_id)
          sort = {direct_conversation.updated_at: "desc", direct_conversation.id: "desc"}

                  return = {type: "list", paging: {page: $p.page, per_page: 20, metadata: true}}

                  output = ["items.id", "items.updated_at", "items.messages", "items.tutor_name", "items.veterinarian_name", "nextPage", "curPage"]
        } as $rows
        api.lambda {
          code = """
            const rows=$var.rows,profile=$input.profile;
            return {threads:(Array.isArray(rows)?rows:rows.items||[]).map(r=>{
              const messages=r.messages||[],last=messages[messages.length-1];
              return {id:r.id,peer:{profile:profile==='tutor'?'veterinario':'tutor',name:profile==='tutor'?r.veterinarian_name:r.tutor_name},updated_at:r.updated_at,
                unread:messages.filter(m=>m.author_profile!==profile&&!m.read_at&&!m.deleted_at).length,
                last_message:last?{text:last.deleted_at?'Mensagem apagada':last.text.slice(0,120),at:last.at}:null};
            }),page:$var.p.page,has_next:!Array.isArray(rows)&&rows.nextPage!=null};
            """
        } as $reply
      }
      else {
        db.transaction {
          stack {
            api.lambda {
              code = "return $var.p.action==='start'?'direct:pair:'+$var.p.veterinario_id+':'+$var.p.tutor_id:'direct:thread:'+$var.p.thread_id;"
            } as $lock_key
            db.add support_lock { data = {key: $lock_key} } as $guard
            conditional {
              if ($p.action == "start") {
                db.get tutor { field_name = "id"
                  field_value = $p.tutor_id
                  output = ["id"] } as $target
                precondition ($target != null) { error_type = "notfound"
                  error = "Tutor não disponível." }
                db.get veterinario {
                  field_name = "id"
                  field_value = $p.veterinario_id
                  output = ["id"]
                } as $target_vet
                precondition ($target_vet != null) {
                  error_type = "notfound"
                  error = "Veterinário não disponível."
                }
                api.lambda { code = "return $var.p.veterinario_id+':'+$var.p.tutor_id;" } as $pair_key
                db.query direct_conversation { where = $db.direct_conversation.pair_key == $pair_key
                  return = {type: "single"} } as $thread
                conditional {
                  if ($thread == null) {
                    db.add direct_conversation {
                      data = {pair_key: $pair_key, tutor_id: $p.tutor_id, veterinario_id: $p.veterinario_id, messages: [], events: [], updated_at: "now"}
                    } as $thread
                  }
                }
              }
              else {
                db.get direct_conversation { field_name = "id"
                  field_value = $p.thread_id } as $thread
              }
            }
            precondition ($thread != null) { error_type = "notfound"
                  error = "Conversa não disponível." }
            precondition (($input.profile == "tutor" && $thread.tutor_id == $input.actor_id) || ($input.profile == "veterinario" && $thread.veterinario_id == $input.actor_id)) {
              error_type = "accessdenied"

                  error = "Conversa não disponível."
            }
            api.lambda {
              code = """

                const p=$var.p,t=$var.thread,profile=$input.profile,actor=$input.actor_id;
                let messages=t.messages||[],events=t.events||[];
                const existing=events.find(e=>e.operation_id&&e.operation_id===p.operation_id);
                const mutation=['edit','delete'].includes(p.action);
                const requestValue=mutation?JSON.stringify({message_id:p.message_id,expected_revision:p.expected_revision,...(p.action==='edit'?{message:p.message}:{})}):(p.action==='send'?p.message:p.reason);
                const previousValue=p.action==='send'?messages.find(m=>m.id===p.operation_id)?.text:mutation?existing?.value?.request:existing?.value;
                if(existing&&(existing.actor_id!==actor||existing.actor_profile!==profile||existing.action!==p.action||previousValue!==requestValue))throw Error('Operação já utilizada.');
                let mutationAudit=null;
                if(mutation){
                  const index=messages.findIndex(m=>m.id===p.message_id),message=messages[index];
                  if(!message||message.author_profile!==profile||message.author_id!==actor)throw Error('Mensagem não disponível.');
                  if(!existing){
                    if(message.deleted_at)throw Error('Mensagem não disponível.');
                    const age=Date.now()-message.at;
                    if(!Number.isFinite(message.at)||age<0||age>600000)throw Error('O prazo de 10 minutos para editar ou apagar esta mensagem terminou.');
                    if((message.revision||0)!==p.expected_revision)throw Error('A mensagem foi alterada. Atualize a conversa antes de tentar novamente.');
                    mutationAudit={request:requestValue,message_id:message.id,previous_text:message.text,previous_revision:message.revision||0};
                    const now=Date.now();
                    messages=messages.map((m,i)=>i===index?(p.action==='edit'?{...m,text:p.message,revision:(m.revision||0)+1,edited_at:now,read_at:null}:{...m,text:'',revision:(m.revision||0)+1,deleted_at:now}):m);
                  }
                }
                if(!existing&&p.action==='send'){
                  messages=[...messages,{id:p.operation_id,author_profile:profile,author_id:actor,text:p.message,at:Date.now()}];
                }
                const operationChanged=!existing&&['send','edit','delete'].includes(p.action);
                if(operationChanged)events=[...events,{id:events.length+1,action:p.action,at:Date.now(),actor_id:actor,actor_profile:profile,operation_id:p.operation_id||null,value:mutation?mutationAudit:''}];
                let readChanged=false;
                if(p.read_through){
                  const end=messages.findIndex(m=>m.id===p.read_through&&m.author_profile!==profile);
                  if(end<0)throw Error('Confirmação de leitura inválida.');
                  const now=Date.now();
                  const expectedReadRevision=p.read_revision||0;
                  const validTarget=!messages[end].deleted_at&&(messages[end].revision||0)===expectedReadRevision;
                  messages=messages.map((m,i)=>{
                    if(validTarget&&i<=end&&m.author_profile!==profile&&!m.deleted_at&&!m.read_at&&((m.revision||0)===0||i===end)){readChanged=true;return {...m,read_at:now};}
                    return m;
                  });
                }
                return {changed:operationChanged||readChanged,messages,events};

                """
            } as $next
            conditional {
              if ($next.changed) {
                db.edit direct_conversation {
                  field_name = "id"

                  field_value = $thread.id
                  data = {messages: $next.messages, events: $next.events, updated_at: "now"}
                } as $thread
              }
            }
            db.get tutor { field_name = "id"
                  field_value = $thread.tutor_id
                  output = ["nome"] } as $tutor
            db.get veterinario { field_name = "id"
                  field_value = $thread.veterinario_id
                  output = ["nome", "crmv", "cmv", "crmv_uf"] } as $vet
            api.lambda {
              code = """
                const t=$var.thread,v=$var.vet,u=$var.tutor;
                return {server_time:Date.now(),thread:{id:t.id,created_at:t.created_at,updated_at:t.updated_at,tutor:{name:u?.nome||''},veterinarian:{name:v?.nome||'',crmv:v?.crmv||v?.cmv||'',uf:v?.crmv_uf||''},messages:t.messages||[]}};
                """
            } as $reply
            db.del support_lock { field_name = "id"
                  field_value = $guard.id }
          }
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "direct-messaging"]
  guid = "53Ye-emWC5O4leaDflBQYOz1GoQ"
}
