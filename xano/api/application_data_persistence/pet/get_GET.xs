query "pets/{pet_id}" verb=GET {
  api_group = "Pet"
  auth = "tutor"

  input {
    int pet_id
  }

  stack {
    precondition ($input.pet_id > 0) {
      error_type = "inputerror"
      error = "Identificador de pet inválido."
    }

    db.query pet {
      where = $db.pet.id == $input.pet_id && $db.pet.tutor_id == $auth.id
      return = {type: "single"}
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
      ]
    } as $pet

    precondition ($pet != null) {
      error_type = "notfound"
      error = "Pet não disponível."
    }
  }

  response = $pet
  guid = "GRNgwcfEX3vB_eCH0s2mAL635n0"
}
