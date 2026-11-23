query "clinica/veterinarios" verb=POST {
  api_group = "Authentication"
  auth = "clinica_admin"
  input {
    text nome filters=trim
    email email filters=trim|lower
    text telefone filters=trim
    password password
    text crmv filters=trim|upper
    text crmv_uf filters=trim|upper
    int[] especies_ids
    int[] especialidades_ids
  }
  stack {
    db.get clinica_admin {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "clinica_id"]
    } as $admin
    precondition ($admin != null && $admin.ativo == true && $admin.clinica_id != null && $admin.clinica_id != 0) {
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
    precondition ($input.password != null && $input.password != "") {
      error_type = "inputerror"
      error = "Informe a senha provisória."
    }
    function.run "Identity/create_veterinario" {
      input = {nome: $input.nome, email: $input.email, telefone: $input.telefone, password: $input.password, crmv: $input.crmv, crmv_uf: $input.crmv_uf, clinica_id: $clinica.id, especies_ids: $input.especies_ids, especialidades_ids: $input.especialidades_ids}
    } as $created
    util.post_process {
      stack {
        var $welcome_attempted {value=false}
        try_catch {
          try {
            function.run "Notifications/send_welcome_email" {input={event_id:$created.event_id}} as $welcome
            var.update $welcome_attempted {value=true}
          }
          catch {
            var.update $welcome_attempted {value=false}
          }
        }
      }
    }
  }
  response = {success: true}
  history = false
  tags = ["vettech"]
}
