query "clinica/veterinarios/convites" verb=POST {
  api_group = "Authentication"
  auth = "clinica_admin"
  input { email email filters=trim|lower }
  stack {
    db.get clinica_admin { field_name = "id" field_value = $auth.id output = ["id", "ativo", "clinica_id"] } as $admin
    precondition ($admin != null && $admin.ativo == true && $admin.clinica_id != null && $admin.clinica_id != 0) { error_type = "accessdenied" error = "Sessão inválida." }
    db.get clinica { field_name = "id" field_value = $admin.clinica_id output = ["id"] } as $clinica
    precondition ($clinica != null) { error_type = "accessdenied" error = "Sessão inválida." }
    db.get veterinario { field_name = "email" field_value = $input.email output = ["id"] } as $vet
    precondition ($vet != null) { error_type = "inputerror" error = "Profissional indisponível para vínculo." }
    db.transaction {
      stack {
        db.add veterinario_vinculo_lock { data = {veterinario_id: $vet.id} } as $guard
        db.get veterinario { field_name = "id" field_value = $vet.id output = ["id", "clinica_id"] } as $current
        precondition ($current != null && ($current.clinica_id == null || $current.clinica_id == 0)) { error_type = "inputerror" error = "Profissional indisponível para vínculo." }
        db.query clinica_veterinario_convite {
          where = $db.clinica_veterinario_convite.veterinario_id == $vet.id && $db.clinica_veterinario_convite.clinica_id == $clinica.id && $db.clinica_veterinario_convite.status == "pendente"
          return = {type: "single"}
        } as $existing
        conditional {
          if ($existing == null) {
            db.add clinica_veterinario_convite { data = {clinica_id: $clinica.id, veterinario_id: $vet.id, admin_id: $admin.id, status: "pendente"} } as $invite
          }
        }
        db.del veterinario_vinculo_lock { field_name = "id" field_value = $guard.id }
      }
    }
  }
  response = {success: true}
  tags = ["vettech"]
}
