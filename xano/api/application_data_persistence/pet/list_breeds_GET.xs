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
      output = ["id", "nome", "especie_id"]
      return = {type: "list"}
    } as $racas
  }

  response = $racas
}