// Caller must have acquired clinical_lock in its transaction before clinical IO.
function "Clinical/assert_access" {
  input {
    int pet_id
    int veterinario_id
  }
  stack {
    db.query acesso_autorizado {
      where = $db.acesso_autorizado.pet_id == $input.pet_id && $db.acesso_autorizado.veterinario_id == $input.veterinario_id && $db.acesso_autorizado.status == "ativo"
      return = {
        type: "single"
      }
    } as $consent
    precondition ($consent != null) {
      error_type = "accessdenied"
      error = "Acesso clínico não disponível. Verifique a autorização do tutor."
    }
    db.get pet {
      field_name = "id"
      field_value = $input.pet_id
      output = ["id", "nome", "especie_id", "tutor_id", "sexo", "data_nasc", "peso_atual", "raca_id"]
    } as $authorized_pet
    precondition ($authorized_pet != null) {
      error_type = "notfound"
      error = "Pet não disponível."
    }
  }
  response = $authorized_pet
  tags = ["vettech", "clinical"]
  guid = "7x1PiyU-aA3woa2AJQ3RAqmGM0U"
}
