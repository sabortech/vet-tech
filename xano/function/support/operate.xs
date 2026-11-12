function "Support/operate" {
  input {
    text profile
    int actor_id
    json payload
  }
  stack {
    api.lambda {
      code = """
        const p=$input.payload;
        const uuid=v=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(v);
        if(!p||!['list','get','create','claim','send','close'].includes(p.action))throw Error('Operação inválida.');
        if(p.action==='create'&&($input.profile!=='tutor'||!uuid(p.conversation_id)||p.consent!==true||!Number.isInteger(p.pet_id)||!p.reason||typeof p.reason!=='string'||p.reason.length>1000||!Array.isArray(p.context)||!p.context.length||p.context.some(m=>!['user','assistant'].includes(m.role)||typeof m.content!=='string')))throw Error('Encaminhamento inválido.');
        if(['get','claim','send','close'].includes(p.action)&&(!Number.isInteger(p.ticket_id)||p.ticket_id<1))throw Error('Chamado inválido.');
        if(['send','close'].includes(p.action)&&!uuid(p.operation_id))throw Error('Operação inválida.');
        if(p.action==='send'&&(typeof p.message!=='string'||!p.message.trim()||p.message.length>1000))throw Error('Mensagem inválida.');
        if(p.action==='close'&&(typeof p.reason!=='string'||!p.reason.trim()||p.reason.length>1000||!['aguardando','em_atendimento'].includes(p.expected_status)))throw Error('Motivo ou estado inválido.');
        return p;
        """
      timeout = 5
    } as $p
    var $reply { value = null }
    conditional {
      if ($p.action == "list") {
        db.query support_ticket {
          join = {
            pet: {
              table: "pet"
              where: $db.support_ticket.pet_id == $db.pet.id
            }
          }
          where = $db.pet.tutor_id == $db.support_ticket.tutor_id && (($input.profile == "tutor" && $db.support_ticket.tutor_id == $input.actor_id) || ($input.profile == "veterinario" && ($db.support_ticket.status == "aguardando" || $db.support_ticket.veterinario_id == $input.actor_id)))
          sort = {support_ticket.created_at: "asc"}
          output = ["id", "created_at", "updated_at", "status", "veterinario_id", "tutor_id", "events"]
          return = {type: "list"}
        } as $rows
        api.lambda {
          code = """
            return {tickets:$var.rows.map(r=>{
              const own=$input.profile==='tutor'?r.tutor_id===$input.actor_id:r.veterinario_id===$input.actor_id;
              return {id:r.id,created_at:r.created_at,updated_at:r.updated_at,status:r.status,own,
                events:own?(r.events||[]).map(({id,action,at,actor_profile})=>({id,action,at,actor_profile})):[]};
            })};
            """
        } as $listed
        var.update $reply { value = $listed }
      }
      else {
        db.transaction {
          stack {
            api.lambda {
              code = """
                return $var.p.action==='create'?'conversation:'+$var.p.conversation_id:'ticket:'+$var.p.ticket_id;
                """
            } as $lock_key
            db.add support_lock { data = {key: $lock_key} } as $guard
            conditional {
              if ($p.action == "create") {
                function.run "Clinical/assert_owner" {
                  input = {pet_id: $p.pet_id, tutor_id: $input.actor_id}
                } as $owned
                db.query support_ticket {
                  where = $db.support_ticket.conversation_id == $p.conversation_id
                  return = {type: "single"}
                } as $ticket
                conditional {
                  if ($ticket == null) {
                    api.lambda {
                      code = """
                        const now=Date.now();
                        return [{id:1,action:'create',at:now,actor_id:$input.actor_id,actor_profile:$input.profile}];
                        """
                    } as $events
                    db.add support_ticket {
                      data = {tutor_id: $input.actor_id, pet_id: $p.pet_id, conversation_id: $p.conversation_id, status: "aguardando", reason: $p.reason, context: $p.context, messages: [], events: $events, updated_at: "now"}
                    } as $ticket
                  }
                }
                precondition ($ticket.tutor_id == $input.actor_id && $ticket.pet_id == $p.pet_id) {
                  error_type = "accessdenied"
                  error = "Chamado não disponível."
                }
              }
              else {
                db.get support_ticket {
                  field_name = "id"
                  field_value = $p.ticket_id
                } as $ticket
              }
            }
            precondition ($ticket != null) {
              error_type = "notfound"
              error = "Chamado não disponível."
            }
            precondition (($input.profile == "tutor" && $ticket.tutor_id == $input.actor_id) || ($input.profile == "veterinario" && ($ticket.veterinario_id == $input.actor_id || ($p.action == "claim" && $ticket.status == "aguardando")))) {
              error_type = "accessdenied"
              error = "Chamado não disponível."
            }
            // Ownership remains mandatory even after a pet changes tutor.
            db.get pet {
              field_name = "id"
              field_value = $ticket.pet_id
            } as $pet
            precondition ($pet != null && $pet.tutor_id == $ticket.tutor_id) {
              error_type = "accessdenied"
              error = "Chamado não disponível."
            }
            api.lambda {
              code = """
                const p=$var.p,t=$var.ticket,profile=$input.profile,actor=$input.actor_id;
                let status=t.status,vet=t.veterinario_id,messages=t.messages||[],events=t.events||[];
                const existing=events.find(e=>e.operation_id&&e.operation_id===p.operation_id);
                const previousValue=p.action==='send'?messages.find(m=>m.id===p.operation_id)?.text:existing?.value;
                if(existing&&(existing.actor_id!==actor||existing.actor_profile!==profile||existing.action!==p.action||previousValue!==(p.action==='send'?p.message:p.reason)))throw Error('Operação já utilizada.');
                if(!existing&&p.action==='claim'){
                  if(profile!=='veterinario'||status!=='aguardando')throw Error('Chamado já assumido ou encerrado.');
                  vet=actor;status='em_atendimento';
                }
                if(!existing&&p.action==='send'){
                  if(status!=='em_atendimento')throw Error('Chamado não está em atendimento.');
                  messages=[...messages,{id:p.operation_id,author_profile:profile,author_id:actor,text:p.message,at:Date.now()}];
                }
                if(!existing&&p.action==='close'){
                  if(p.expected_status!==status)throw Error('O chamado mudou. Atualize antes de encerrar.');
                  if(status==='encerrado'||(status==='aguardando'&&profile!=='tutor'))throw Error('Chamado encerrado ou indisponível.');
                  status='encerrado';
                }
                const changed=!existing&&['claim','send','close'].includes(p.action);
                if(changed)events=[...events,{id:events.length+1,action:p.action,at:Date.now(),actor_id:actor,actor_profile:profile,operation_id:p.operation_id||null,value:p.action==='close'?p.reason:''}];
                return {changed,status,veterinario_id:vet||null,messages,events};
                """
            } as $next
            conditional {
              if ($next.changed) {
                db.edit support_ticket {
                  field_name = "id"
                  field_value = $ticket.id
                  data = {status: $next.status, veterinario_id: $next.veterinario_id, messages: $next.messages, events: $next.events, updated_at: "now"}
                } as $ticket
              }
            }
            var $vet { value = null }
            conditional {
              if ($ticket.veterinario_id != null) {
                db.get veterinario {
                  field_name = "id"
                  field_value = $ticket.veterinario_id
                } as $vet
              }
            }
            api.lambda {
              code = """
                const t=$var.ticket,v=$var.vet;
                return {ticket:{id:t.id,pet:{id:$var.pet.id,name:$var.pet.nome},status:t.status,reason:t.reason,
                  veterinarian:v?{name:v.nome,crmv:v.crmv||v.cmv,uf:v.crmv_uf}:null,
                  context:t.context,messages:t.messages,created_at:t.created_at,
                  events:(t.events||[]).map(({value,...e})=>({...e,reason:e.action==='close'?value:undefined}))}};
                """
            } as $projected
            var.update $reply { value = $projected }
            db.del support_lock {
              field_name = "id"
              field_value = $guard.id
            }
          }
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "support-chat"]
  guid = "3Qw9AdQNB6Wf7HPKdjk9ArYslYQ"
}
