function "Clinical/assert_owner" {
  input {
    int pet_id
    int tutor_id
  }
  stack {
    db.query pet {
      where = $db.pet.id == $input.pet_id && $db.pet.tutor_id == $input.tutor_id
      output = ["id", "nome", "especie_id", "tutor_id"]
      return = {
        type: "single"
      }
    } as $owned_pet
    precondition ($owned_pet != null) {
      error_type = "notfound"
      error = "Pet não disponível."
    }
  }
  response = $owned_pet
  tags = ["vettech", "clinical"]
  guid = "hJj0ipFl1kfNFkvcZsSldMEptSs"
}
