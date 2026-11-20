query "adoption" verb=POST {
  api_group = "Pet"
  auth = "tutor"

  input {
    int pet_id
  }

  stack {
    db.get tutor {
      field_name = "id"
      field_value = $auth.id
      output = ["id"]
    } as $tutor

    precondition ($tutor != null) {
      error_type = "accessdenied"
      error = "Tutor não autenticado."
    }

    precondition ($input.pet_id > 0) {
      error_type = "inputerror"
      error = "Identificador de pet inválido."
    }

    db.get pet {
      field_name = "id"
      field_value = $input.pet_id
      output = ["id", "disponivel_adocao"]
    } as $candidate

    precondition ($candidate != null && $candidate.disponivel_adocao == true) {
      error_type = "notfound"
      error = "Pet não disponível."
    }

    var $adopted {
      value = null
    }

    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $clinical_guard

        db.get pet {
          field_name = "id"
          field_value = $input.pet_id
          output = ["id", "disponivel_adocao", "tutor_id", "clinica_id"]
        } as $locked_pet

        precondition ($locked_pet != null && $locked_pet.disponivel_adocao == true) {
          error_type = "notfound"
          error = "Pet não disponível."
        }

        precondition ((($locked_pet.tutor_id != null && $locked_pet.tutor_id > 0) && ($locked_pet.clinica_id == null || $locked_pet.clinica_id == 0)) || (($locked_pet.clinica_id != null && $locked_pet.clinica_id > 0) && ($locked_pet.tutor_id == null || $locked_pet.tutor_id == 0))) {
          error_type = "inputerror"
          error = "Pet não disponível."
        }

        db.query acesso_autorizado {
          where = $db.acesso_autorizado.pet_id == $input.pet_id && $db.acesso_autorizado.status == "ativo"
          return = {type: "list"}
          output = ["id"]
        } as $active_authorizations

        foreach ($active_authorizations) {
          each as $authorization {
            db.edit acesso_autorizado {
              field_name = "id"
              field_value = $authorization.id
              data = {
                status: "revogado"
                revogado_em: "now"
              }
            } as $revoked_authorization
          }
        }

        db.edit pet {
          field_name = "id"
          field_value = $locked_pet.id
          data = {
            tutor_id: $auth.id
            clinica_id: 0
            disponivel_adocao: false
          }
        } as $updated_pet

        db.query pet {
          join = {
            especie: {
              table: "especie"
              type: "left"
              where: $db.pet.especie_id == $db.especie.id
            }
            raca: {
              table: "raca"
              type: "left"
              where: $db.pet.raca_id == $db.raca.id
            }
          }
          eval = {
            especie_nome: $db.especie.nome
            raca_nome: $db.raca.nome
          }
          where = $db.pet.id == $updated_pet.id
          output = [
            "id"
            "nome"
            "especie_id"
            "raca_id"
            "sexo"
            "data_nasc"
            "peso_atual"
            "foto"
            "especie_nome"
            "raca_nome"
          ]
          return = {type: "single"}
        } as $adopted_pet

        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }

        var.update $adopted {
          value = $adopted_pet
        }
      }
    }
  }

  response = $adopted
  tags = ["vettech"]
  guid = "Wxi6vhXz-DiTs-COmHc4cFztxvU"
}
