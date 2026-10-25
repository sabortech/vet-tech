query "tutor/pets/{pet_id}/acessos" verb=GET {
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
    db.query acesso_autorizado {
      where = $db.acesso_autorizado.pet_id == $owned.id
      output = ["id", "pet_id", "veterinario_id", "status", "concedido_em", "revogado_em"]
      return = {
        type: "list"
      }
    } as $reply
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "ll3NPk0_bIrG4VtFNj_Qi0e5quo"
}
