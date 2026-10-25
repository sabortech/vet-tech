query "veterinario/consultas/{consulta_id}/iniciar" verb=POST {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    int consulta_id
  }
  stack {
    function.run "Clinical/assert_consultation" {
      input = {
        consulta_id: $input.consulta_id, veterinario_id: $auth.id
      }
    } as $consult
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {
            pet_id: $consult.pet_id
          }
        } as $clinical_guard
        function.run "Clinical/assert_consultation" {
          input = {
            consulta_id: $input.consulta_id, veterinario_id: $auth.id
          }
        } as $consult
        function.run "Clinical/assert_access" {
          input = {
            pet_id: $consult.pet_id, veterinario_id: $auth.id
          }
        } as $authorized
        precondition ($consult.status == "agendada" || $consult.status == "em_atendimento") {
          error_type = "inputerror"
          error = "A consulta não pode ser iniciada."
        }
        conditional {
          if ($consult.status == "agendada") {
            db.edit consulta {
              field_name = "id"
              field_value = $consult.id
              data = {
                status: "em_atendimento", iniciada_em: "now", versao: $consult.versao + 1
              }
            } as $started
            function.run "Clinical/audit" {
              input = {
                pet_id: $consult.pet_id, consulta_id: $consult.id, veterinario_id: $auth.id, acao: "iniciar", operacao: null
              }
            } as $audit_event
          }
        }
        var.update $reply {
          value = {
            id: $consult.id, status: "em_atendimento"
          }
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
  guid = "Yi_jJ81dVHW_1WkdZzrL7taW5Ew"
}
