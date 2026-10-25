// Public, explicitly projected non-personal options for registration only.
query "cadastro/opcoes" verb=GET {
  api_group = "Authentication"

  input {
  }

  stack {
    db.query especie {
      return = {type: "list"}
      output = ["id", "nome"]
    } as $species

    db.query especialidade {
      return = {type: "list"}
      output = ["id", "nome"]
    } as $specialties

    db.query clinica {
      return = {type: "list"}
      output = ["id", "nome"]
    } as $clinics
  }

  response = {
    especies      : $species
    especialidades: $specialties
    clinicas      : $clinics
  }

  tags = ["vettech"]
  guid = "aDTfRpvIi9Rck7x_3Tn3MGD-hmg"
}
