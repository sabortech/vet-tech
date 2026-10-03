query "catalog/racas" verb=GET {
  api_group = "Pet"
  auth = "tutor"

  input {
    int especie_id
  }

  stack {
    db.query raca {
      where = $this.especie_id == $input.especie_id
      sort = {nome: "asc"}
      return = {type: "list"}
      output = ["id", "nome", "especie_id"]
    } as $racas
  }

  response = $racas
  guid = "2XTdbjSMWu-KwQEU45-p3KxeI7s"
}