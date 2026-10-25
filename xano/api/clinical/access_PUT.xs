query "tutor/pets/{pet_id}/acessos/{acesso_id}" verb=PUT {
  api_group = "Clinical"
  auth = "tutor"
  input {
    int pet_id
    int acesso_id
    text status
  }
  stack {
    function.run "Clinical/assert_owner" {
      input = {
        pet_id: $input.pet_id, tutor_id: $auth.id
      }
    } as $owned
    precondition ($input.status == "ativo" || $input.status == "revogado") {
      error_type = "inputerror"
      error = "Estado de autorização inválido."
    }
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {
            pet_id: $owned.id
          }
        } as $clinical_guard
        db.query acesso_autorizado {
          where = $db.acesso_autorizado.id == $input.acesso_id && $db.acesso_autorizado.pet_id == $owned.id
          return = {
            type: "single"
          }
        } as $consent
        precondition ($consent != null) {
          error_type = "notfound"
          error = "Autorização não disponível."
        }
        var $revoked {
          value = null
        }
        conditional {
          if ($input.status == "revogado") {
            var.update $revoked {
              value = "now"
            }
          }
        }
        db.edit acesso_autorizado {
          field_name = "id"
          field_value = $consent.id
          data = {
            status: $input.status, revogado_em: $revoked
          }
        } as $updated
        function.run "Clinical/audit" {
          input = {
            pet_id: $owned.id, veterinario_id: $consent.veterinario_id, tutor_id: $auth.id, acao: $input.status
          }
        } as $consent_audit
        var.update $reply {
          value = {
            id: $updated.id, status: $updated.status
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
  guid = "rK3KcGIQ6X5WxEqBO2kRRmtuV-4"
}
