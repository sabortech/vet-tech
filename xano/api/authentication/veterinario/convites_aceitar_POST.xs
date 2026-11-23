query "veterinario/convites/aceitar" verb=POST {
  api_group = "Authentication"
  auth = "veterinario"
  input { int convite_id }
  stack {
    db.transaction {
      stack {
        db.add veterinario_vinculo_lock { data = {veterinario_id: $auth.id} } as $guard
        db.get veterinario { field_name = "id" field_value = $auth.id output = ["id", "clinica_id"] } as $vet
        db.get clinica_veterinario_convite { field_name = "id" field_value = $input.convite_id } as $invite
        precondition ($vet != null && ($vet.clinica_id == null || $vet.clinica_id == 0) && $invite != null && $invite.veterinario_id == $auth.id && $invite.status == "pendente") { error_type = "accessdenied" error = "Convite indisponível." }
        db.get clinica { field_name = "id" field_value = $invite.clinica_id output = ["id"] } as $clinica
        precondition ($clinica != null) { error_type = "accessdenied" error = "Convite indisponível." }
        db.edit veterinario { field_name = "id" field_value = $vet.id data = {clinica_id: $clinica.id} } as $updated
        db.edit clinica_veterinario_convite { field_name = "id" field_value = $invite.id data = {status: "aceito"} } as $accepted
        db.del veterinario_vinculo_lock { field_name = "id" field_value = $guard.id }
      }
    }
  }
  response = {success: true}
  tags = ["vettech"]
}
