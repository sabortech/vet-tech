query "authorizations" verb=PUT {
  api_group = "Prontuario"
  auth = "tutor"
  input {
    int pet_id
    int veterinario_id
    text status filters=trim
  }
  stack {
    function.run "records/require_owner" {
      input = {tutor_id: $auth.id, pet_id: $input.pet_id}
    } as $pet
    precondition ($input.status == "ativo" || $input.status == "revogado") {
      error_type = "inputerror"
      error = "Status inválido."
    }
    db.get veterinario {
      field_name = "id"
      field_value = $input.veterinario_id
      output = ["id"]
    } as $veterinario
    precondition ($veterinario != null) {
      error_type = "inputerror"
      error = "Veterinário inválido."
    }
    var $autorizacao {
      value = null
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $clinical_guard
        db.query acesso_autorizado {
          where = $db.acesso_autorizado.pet_id == $input.pet_id && $db.acesso_autorizado.veterinario_id == $input.veterinario_id
          return = {type: "single"}
        } as $existente
        conditional {
          if ($existente != null) {
            db.edit acesso_autorizado {
              field_name = "id"
              field_value = $existente.id
              data = {status: $input.status}
            } as $atualizada
            var.update $autorizacao {
              value = $atualizada
            }
          }
          else {
            db.add acesso_autorizado {
              data = {pet_id: $input.pet_id, veterinario_id: $input.veterinario_id, status: $input.status, data_autorizacao: "now"}
            } as $nova
            var.update $autorizacao {
              value = $nova
            }
          }
        }
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
      }
    }
  }
  response = $autorizacao
  guid = "uxbSgHrVZdGnTXTFQyXWYsfECOM"
}
