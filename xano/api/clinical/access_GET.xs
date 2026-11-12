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
      join = {
        veterinario: {
          table: "veterinario"
          type: "left"
          where: $db.acesso_autorizado.veterinario_id == $db.veterinario.id
        }
      }
      eval = {veterinario_nome: $db.veterinario.nome}
      where = $db.acesso_autorizado.pet_id == $owned.id
      output = ["id", "pet_id", "veterinario_id", "veterinario_nome", "status", "concedido_em", "revogado_em"]
      return = {
        type: "list"
      }
    } as $reply
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "ll3NPk0_bIrG4VtFNj_Qi0e5quo"
}
