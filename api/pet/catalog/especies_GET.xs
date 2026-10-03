query "catalog/especies" verb=GET {
  api_group = "Pet"
  auth = "tutor"

  input {
  }

  stack {
    db.query especie {
      sort = {nome: "asc"}
      return = {type: "list"}
      output = ["id", "nome"]
    } as $especies
  }

  response = $especies
  guid = "vhziwLPPtwIRXt_gyj9T_i4dR4I"
}