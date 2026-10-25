query "tutor/me" verb=GET {
  api_group = "Authentication"
  auth = "tutor"
  input {}
  stack {
    db.get tutor {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "nome"]
    } as $identity
    precondition ($identity != null) { error_type = "accessdenied"
      error = "Sessão inválida." }
  }
  response = {perfil: "tutor", identidade_id: $identity.id, nome: $identity.nome}
  tags = ["vettech"]
  guid = "rS1O7dpCNQN-0WHfrUcqfL48T2M"
}
