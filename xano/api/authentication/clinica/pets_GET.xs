query "clinica/pets" verb=GET {
  api_group = "Authentication"
  auth = "clinica_admin"
  input {
  }
  stack {
    db.get clinica_admin {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "clinica_id"]
    } as $admin
    precondition ($admin != null && $admin.ativo == true && $admin.clinica_id != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    db.get clinica {
      field_name = "id"
      field_value = $admin.clinica_id
      output = ["id"]
    } as $clinica
    precondition ($clinica != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    db.query pet {
      where = $db.pet.clinica_id == $clinica.id && ($db.pet.tutor_id == null || $db.pet.tutor_id == 0)
      output = ["id", "nome", "especie_id", "raca_id", "sexo", "data_nasc", "peso_atual", "foto", "disponivel_adocao"]
      return = {type: "list"}
    } as $pets
  }
  response = $pets
  tags = ["vettech"]
}
