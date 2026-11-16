query "veterinario/signup" verb=POST {
  api_group = "Authentication"

  input {
    text nome filters=trim
    email email filters=trim|lower
    text telefone filters=trim
    password password
    text crmv filters=trim|upper
    text crmv_uf filters=trim|upper
    int clinica_id?
    int[] especies_ids
    int[] especialidades_ids
  }

  stack {
    precondition ($input.password != null && $input.password != "") {
      error_type="inputerror"
      error="Preencha todos os campos obrigatórios."
    }
    function.run "Identity/create_veterinario" {
      input={nome:$input.nome, email:$input.email, telefone:$input.telefone, password:$input.password, crmv:$input.crmv, crmv_uf:$input.crmv_uf, clinica_id:$input.clinica_id, especies_ids:$input.especies_ids, especialidades_ids:$input.especialidades_ids}
    } as $created
    // A resposta do cadastro não depende do provedor de e-mail.
    util.post_process {
      stack {
        var $welcome_attempted {value=false}
        try_catch {
          try {
            function.run "Notifications/send_welcome_email" {input={event_id:$created.event_id}} as $welcome_result
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
  guid = "IvZWoi43BQXpjoGEnI3rgEm-U_c"
}
