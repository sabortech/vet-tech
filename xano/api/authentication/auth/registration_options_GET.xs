// Public, explicitly projected non-personal options for registration only.
query "cadastro/opcoes" verb=GET {
  api_group = "Authentication"
  input {}
  stack {
    db.query especie {
      output = ["id", "nome"]
      return = {type: "list"} } as $species
    db.query especialidade {
      output = ["id", "nome"]
      return = {type: "list"} } as $specialties
    db.query clinica {
      output = ["id", "nome"]
      return = {type: "list"} } as $clinics
  }
  response = {especies: $species, especialidades: $specialties, clinicas: $clinics}
  tags = ["vettech"]
  guid = "aDTfRpvIi9Rck7x_3Tn3MGD-hmg"
}
