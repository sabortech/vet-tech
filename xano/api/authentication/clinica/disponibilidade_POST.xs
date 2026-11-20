query "clinica/disponibilidade" verb=POST {
  api_group = "Authentication"
  auth = "clinica_admin"
  input {
    int pet_id
    bool disponivel
  }
  stack {
    db.get clinica_admin {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "clinica_id"]
    } as $admin
    precondition ($admin != null && $admin.ativo == true && $admin.clinica_id != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    db.get clinica {
      field_name = "id"
      field_value = $admin.clinica_id
      output = ["id"]
    } as $clinica
    precondition ($clinica != null && $input.pet_id > 0) {
      error_type = "accessdenied"
      error = "Pet não disponível."
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $guard
        db.get pet {
          field_name = "id"
          field_value = $input.pet_id
          output = ["id", "clinica_id", "tutor_id"]
        } as $pet
        precondition ($pet != null && $pet.clinica_id == $clinica.id && ($pet.tutor_id == null || $pet.tutor_id == 0)) {
          error_type = "notfound"
          error = "Pet não disponível."
        }
        db.edit pet {
          field_name = "id"
          field_value = $pet.id
          data = {disponivel_adocao: $input.disponivel}
        } as $atualizado
        var $acao { value = "retirada" }
        conditional {
          if ($input.disponivel == true) {
            var.update $acao { value = "publicacao" }
          }
        }
        db.add clinica_adocao_evento {
          data = {clinica_id: $clinica.id, admin_id: $admin.id, pet_id: $pet.id, acao: $acao}
        } as $evento
        db.del clinical_lock {
          field_name = "id"
          field_value = $guard.id
        }
      }
    }
  }
  response = {id: $input.pet_id, disponivel_adocao: $input.disponivel}
  tags = ["vettech"]
}
