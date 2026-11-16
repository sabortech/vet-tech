query "tutor/signup" verb=POST {
  api_group = "Authentication"

  input {
    text nome filters=trim
    text cpf filters=trim
    email email filters=trim|lower
    text telefone filters=trim
    text endereco filters=trim
    password password
  }

  stack {
    precondition ($input.password != null && $input.password != "") {
      error_type="inputerror"
      error="Preencha todos os campos obrigatórios."
    }
    function.run "Identity/create_tutor" {
      input={nome:$input.nome, cpf:$input.cpf, email:$input.email, telefone:$input.telefone, endereco:$input.endereco, password:$input.password}
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
  guid = "Sf0P9fazACZFbxFTNcfSQqqKHqY"
}
