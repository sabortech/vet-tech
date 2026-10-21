query "veterinario/me" verb=GET {
  api_group = "Authentication"
  auth = "veterinario"
  input {}
  stack {
    db.get veterinario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "nome"]
    } as $identity
    precondition ($identity != null) { error_type = "accessdenied"
      error = "Sessão inválida." }
  }
  response = {perfil: "veterinario", identidade_id: $identity.id, nome: $identity.nome}
  tags = ["vettech"]
  guid = "fo3wA78S0UpjMSnT2lS2oztodig"
}
