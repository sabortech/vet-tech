query pets verb=GET {
  api_group = "Pet"
  auth = "tutor"

  input {
  }

  stack {
    db.query pet {
      where = $this.tutor_id == $auth.id
      sort = {created_at: "desc"}
      return = {type: "list"}
      output = [
        "id"
        "nome"
        "especie_id"
        "raca_id"
        "sexo"
        "data_nasc"
        "peso_atual"
        "cor_pelo"
        "num_microchip"
        "created_at"
      ]
    } as $pets
  }

  response = $pets
  guid = "oihmBtzQwDfOr2Y6iSA5BWh3N3o"
}