query "tutor/pets/{pet_id}/auditoria" verb=GET {
  api_group = "Clinical"
  auth = "tutor"
  input {
    int pet_id
  }
  stack {
    function.run "Clinical/assert_owner" {
      input = {
        pet_id: $input.pet_id, tutor_id: $auth.id
      }
    } as $owned
    db.query log_acesso {
      where = $db.log_acesso.pet_id == $owned.id
      output = ["id", "veterinario_id", "tutor_id", "consulta_id", "acao", "ocorrido_em", "data_hora"]
      sort = {
        log_acesso.ocorrido_em: "desc"
      }
      return = {
        type: "list"
      }
    } as $reply
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "mzU7oqzL_60Tavu3CEvJ_UkEaBU"
}
