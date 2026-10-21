query "audit" verb=GET {
  api_group = "Prontuario"
  auth = "tutor"
  input {
    int pet_id
  }
  stack {
    function.run "records/require_owner" {
      input = {tutor_id: $auth.id, pet_id: $input.pet_id}
    } as $pet
    db.query log_acesso {
      where = $db.log_acesso.pet_id == $input.pet_id
      return = {type: "list"}
    } as $registros
  }
  response = $registros
}
