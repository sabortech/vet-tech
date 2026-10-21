query "tutor/profissionais" verb=GET {
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
    db.query veterinario_especie {
      where = $db.veterinario_especie.especie_id == $owned.especie_id
      output = ["veterinario_id"]
      return = {
        type: "list"
      }
    } as $links
    db.query veterinario {
      where = $db.veterinario.id > 0
      output = ["id", "nome", "crmv", "crmv_uf"]
      return = {
        type: "list"
      }
    } as $professionals
    api.lambda {
      code = "const ids=new Set($var.links.map(x=>x.veterinario_id));return $var.professionals.filter(x=>ids.has(x.id));"
      timeout = 5
    } as $reply
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "f39buio6ld3qmJO1eoRU7J5Hj98"
}
