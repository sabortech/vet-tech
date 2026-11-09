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
        function.run "Clinical/consultation_document" {
          input = {pet_id: $owned.id, consulta_id: $input.consulta_id, pet_nome: $owned.nome}
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
            precondition ($existing.pet_id == $owned.id && $existing.consulta_id == $input.consulta_id && $existing.tutor_id == $auth.id && $existing.acao == "exportar_consulta") {
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
              input = {pet_id: $owned.id, consulta_id: $input.consulta_id, tutor_id: $auth.id, veterinario_id: $document.consulta.veterinario_id, acao: "exportar_consulta", operacao: $operation_key}
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
