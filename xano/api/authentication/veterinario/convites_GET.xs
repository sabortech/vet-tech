query "veterinario/convites" verb=GET {
  api_group = "Authentication"
  auth = "veterinario"
  input { }
  stack {
    db.get veterinario { field_name = "id" field_value = $auth.id output = ["id", "clinica_id"] } as $vet
    db.query clinica_veterinario_convite {
      join = {clinica: {table: "clinica", where: $db.clinica_veterinario_convite.clinica_id == $db.clinica.id}}
      where = $db.clinica_veterinario_convite.veterinario_id == $auth.id && $db.clinica_veterinario_convite.status == "pendente" && ($vet.clinica_id == null || $vet.clinica_id == 0)
      eval = {clinica_nome: $db.clinica.nome}
      output = ["id", "clinica_nome"]
      return = {type: "list"}
    } as $invites
  }
  response = $invites
  tags = ["vettech"]
}
