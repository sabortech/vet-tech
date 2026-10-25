query "veterinario/pets/{pet_id}/doencas" verb=GET {
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
        db.query doenca {
          where = $db.doenca.pet_id == 0 || $db.doenca.pet_id == null
          output = ["id", "nome", "descricao", "tipo", "gravidade"]
          return = {
            type: "list"
          }
        } as $catalog
        var.update $reply {
          value = $catalog
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
  guid = "eAA8_NfzL_-3wtLg3i3pQfmfENI"
}
