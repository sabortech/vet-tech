query "authorizations" verb=GET {
  api_group = "Prontuario"
  auth = "tutor"
  input {
    int pet_id
  }
  stack {
    function.run "records/require_owner" {
      input = {tutor_id: $auth.id, pet_id: $input.pet_id}
    } as $pet
    db.query acesso_autorizado {
      where = $db.acesso_autorizado.pet_id == $input.pet_id
      return = {type: "list"}
    } as $registros
  }
  response = $registros
  guid = "EARL-EbtIP3PDlCijLt2la_k4Fc"
}
