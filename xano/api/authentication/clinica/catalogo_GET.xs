query "clinica/catalogo" verb=GET {
  api_group = "Authentication"
  auth = "clinica_admin"
  input {
  }
  stack {
    db.get clinica_admin {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "clinica_id", "ativo"]
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
    db.query especie {
      output = ["id", "nome"]
      return = {type: "list"}
    } as $especies
    db.query raca {
      output = ["id", "nome", "especie_id"]
      return = {type: "list"}
    } as $racas
  }
  response = {especies: $especies, racas: $racas}
  tags = ["vettech"]
}
