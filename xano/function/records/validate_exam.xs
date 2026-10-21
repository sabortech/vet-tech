function "records/validate_exam" {
  input {
    int pet_id
    int? consulta_id?
  }
  stack {
    db.get pet {
      field_name = "id"
      field_value = $input.pet_id
      output = ["id"]
    } as $pet
    precondition ($pet != null) {
      error_type = "inputerror"
      error = "Pet inválido."
    }
    conditional {
      if ($input.consulta_id != null) {
        db.get consulta {
          field_name = "id"
          field_value = $input.consulta_id
          output = ["id", "pet_id"]
        } as $consulta
        precondition ($consulta != null) {
          error_type = "inputerror"
          error = "Consulta inválida."
        }
        precondition ($consulta.pet_id == $input.pet_id) {
          error_type = "inputerror"
          error = "A consulta não pertence ao pet."
        }
      }
    }
  }
  response = $pet.id
}
