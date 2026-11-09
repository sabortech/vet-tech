query "veterinario/pets/{pet_id}/consultas/{consulta_id}/exportar" verb=POST {
  api_group = "Clinical"
  auth = "veterinario"
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
      value = "exportar_consulta:veterinario:"|concat:$auth.id|concat:":"|concat:$input.operacao
    }
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $clinical_guard
        // Revalidate consent inside the same transaction as the document and audit.
        function.run "Clinical/assert_access" {
          input = {pet_id: $input.pet_id, veterinario_id: $auth.id}
        } as $owned
        function.run "Clinical/consultation_document" {
          input = {pet_id: $owned.id, consulta_id: $input.consulta_id, pet_nome: $owned.nome}
        } as $document
        db.query log_acesso {
          where = $db.log_acesso.operacao == $operation_key
          output = ["id", "pet_id", "consulta_id", "veterinario_id", "acao"]
          return = {type: "single"}
        } as $existing
        var $audit_id {
          value = null
        }
        conditional {
          if ($existing != null) {
            precondition ($existing.pet_id == $owned.id && $existing.consulta_id == $input.consulta_id && $existing.veterinario_id == $auth.id && $existing.acao == "exportar_consulta") {
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
              input = {pet_id: $owned.id, consulta_id: $input.consulta_id, veterinario_id: $auth.id, acao: "exportar_consulta", operacao: $operation_key}
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
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "clinical"]
}
