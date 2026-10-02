query "catalog/especies" verb=GET {
  api_group = "Pet"
  auth = "tutor"

  input {
  }

  stack {
    db.query especie {
      sort = {nome: "asc"}
      output = ["id", "nome"]
      return = {type: "list"}
    } as $especies
  }

  response = $especies
}