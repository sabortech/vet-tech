query "veterinario/consultas/{consulta_id}/rascunho" verb=GET {
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
        function.run "Clinical/audit" {
          input = {
            pet_id: $consult.pet_id, consulta_id: $consult.id, veterinario_id: $auth.id, acao: "visualizar_rascunho", operacao: null
          }
        } as $audit_event
        var.update $reply {
          value = {
            consulta: $consult, pet: $authorized
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
  guid = "X2D_q2OQK0IAHPfvsmT2ooEkWPw"
}
