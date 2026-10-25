query "veterinario/pets/{pet_id}/doencas" verb=POST {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    int pet_id
    json payload
  }
  stack {
    function.run "Clinical/validate" {
      input = {
        kind: "disease", payload: $input.payload, current_time: "now"
      }
    } as $valid
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
        db.query doenca {
          where = $db.doenca.nome_normalizado == $valid.value.nome_normalizado
          return = {
            type: "single"
          }
        } as $catalog_entry
        conditional {
          if ($catalog_entry == null) {
            db.add doenca {
              data = {
                nome: $valid.value.nome, nome_normalizado: $valid.value.nome_normalizado, descricao: $valid.value.descricao
              }
            } as $created_entry
            var.update $catalog_entry {
              value = $created_entry
            }
          }
        }
        var.update $reply {
          value = {
            id: $catalog_entry.id, nome: $catalog_entry.nome
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
  guid = "bfyJU1UwGtloDz7d1xbFy_EZVeg"
}
