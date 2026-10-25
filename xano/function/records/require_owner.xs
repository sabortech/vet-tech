function "records/require_owner" {
  input {
    int tutor_id
    int pet_id
  }

  stack {
    db.get tutor {
      field_name = "id"
      field_value = $input.tutor_id
      output = ["id"]
    } as $tutor

    precondition ($tutor != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.get pet {
      field_name = "id"
      field_value = $input.pet_id
      output = ["id", "tutor_id"]
    } as $pet

    precondition ($pet != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    precondition ($pet.tutor_id == $input.tutor_id) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  }

  response = $pet
  guid = "YjrTrgiBg7VQxhFW4ciLsR8jeLA"
}
