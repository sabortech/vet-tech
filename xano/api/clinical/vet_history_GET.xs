query "veterinario/pets/{pet_id}/historico" verb=GET {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    int pet_id
  }
  stack {
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {
            pet_id: $input.pet_id
          }
        } as $clinical_guard
        function.run "Clinical/assert_access" {
          input = {
            pet_id: $input.pet_id, veterinario_id: $auth.id
          }
        } as $authorized
        function.run "Clinical/history" {
          input = {
            pet_id: $input.pet_id
          }
        } as $history
        function.run "Clinical/audit" {
          input = {
            pet_id: $input.pet_id, consulta_id: null, veterinario_id: $auth.id, acao: "visualizar_historico", operacao: null
          }
        } as $audit_event
        var.update $reply {
          value = {
            pet: $authorized, historico: $history
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
  guid = "4UF3KLMHMNHbafQ8H8YoxhSU4ec"
}
