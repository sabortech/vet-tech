query "tutor/pets/{pet_id}/consultas/{consulta_id}/exportar" verb=POST {
  api_group = "Clinical"
  auth = "tutor"
  input {
    int pet_id
    int consulta_id
    text operacao filters=trim
  }
  stack {
    api.lambda {
      code = "return Number.isInteger($input.pet_id)&&$input.pet_id>0&&Number.isInteger($input.consulta_id)&&$input.consulta_id>0&&/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test($input.operacao);"
      timeout = 5
    } as $valid
    precondition ($valid) {
      error_type = "inputerror"
      error = "Operação inválida."
    }
    var $operation_key {
      value = "exportar_consulta:"|concat:$auth.id|concat:":"|concat:$input.operacao
    }
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        // Revalidate inside the transaction, including on replay.
        function.run "Clinical/assert_owner" {
          input = {pet_id: $input.pet_id, tutor_id: $auth.id}
        } as $owned
        db.query consulta {
          where = $db.consulta.id == $input.consulta_id && $db.consulta.pet_id == $owned.id
          output = ["id", "pet_id", "veterinario_id", "status"]
          return = {type: "single"}
        } as $consult
        precondition ($consult != null) {
          error_type = "notfound"
          error = "Consulta não disponível."
        }
        precondition ($consult.status == "finalizada") {
          error_type = "inputerror"
          error = "Somente consultas finalizadas podem ser exportadas."
        }
        function.run "Clinical/history" {
          input = {pet_id: $owned.id}
        } as $history
        api.lambda {
          code = "const c=$var.history.consultas.find(r=>r.id===$input.consulta_id&&r.pet_id===$input.pet_id&&r.status==='finalizada'); if(!c)throw new Error('Consulta não disponível.'); const result={consulta:c,pet:{id:$var.owned.id,nome:$var.owned.nome}}; for(const k of ['vacinas','medicamentos','diagnosticos','exames'])result[k]=$var.history[k].filter(r=>r.consulta_id===c.id&&r.pet_id===c.pet_id); return result;"
          timeout = 5
        } as $document
        db.query log_acesso {
          where = $db.log_acesso.operacao == $operation_key
          output = ["id", "pet_id", "consulta_id", "tutor_id", "acao"]
          return = {type: "single"}
        } as $existing
        var $audit_id {
          value = null
        }
        conditional {
          if ($existing != null) {
            precondition ($existing.pet_id == $owned.id && $existing.consulta_id == $consult.id && $existing.tutor_id == $auth.id && $existing.acao == "exportar_consulta") {
              error_type = "inputerror"
              error = "A operação já foi usada com dados diferentes."
            }
            var.update $audit_id {
              value = $existing.id
            }
          }
          else {
            // The existing unique index on operacao arbitrates concurrent inserts.
            // A losing request fails closed; its retry revalidates and reads this log.
            function.run "Clinical/audit" {
              input = {pet_id: $owned.id, consulta_id: $consult.id, tutor_id: $auth.id, veterinario_id: $consult.veterinario_id, acao: "exportar_consulta", operacao: $operation_key}
            } as $created_audit
            var.update $audit_id {
              value = $created_audit
            }
          }
        }
        api.lambda {
          code = "return {...$var.document,auditoria_id:$var.audit_id};"
          timeout = 5
        } as $authorized_document
        var.update $reply {
          value = $authorized_document
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "I4cRji-1D6CznKtfr1eN7WXS3yE"
}
