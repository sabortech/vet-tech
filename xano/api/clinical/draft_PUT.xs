query "veterinario/consultas/{consulta_id}/rascunho" verb=PUT {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    int consulta_id
    int versao
    json payload
  }
  stack {
    function.run "Clinical/assert_consultation" {
      input = {
        consulta_id: $input.consulta_id, veterinario_id: $auth.id
      }
    } as $consult
    function.run "Clinical/validate" {
      input = {
        kind: "draft", payload: $input.payload, current_time: "now"
      }
    } as $valid
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
        precondition ($consult.status == "em_atendimento") {
          error_type = "inputerror"
          error = "Consulta não está em atendimento."
        }
        precondition ($consult.versao == $input.versao) {
          error_type = "inputerror"
          error = "A consulta foi alterada em outra sessão. Atualize antes de salvar."
        }
        db.edit consulta {
          field_name = "id"
          field_value = $consult.id
          data = {
            rascunho: $valid.value, versao: $consult.versao + 1
          }
        } as $saved
        function.run "Clinical/audit" {
          input = {
            pet_id: $consult.pet_id, consulta_id: $consult.id, veterinario_id: $auth.id, acao: "salvar_rascunho", operacao: null
          }
        } as $audit_event
        var.update $reply {
          value = {
            id: $saved.id, versao: $saved.versao, status: $saved.status
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
  guid = "sSkTvDlnzQPRLawFWdaIZi5PRdY"
}
