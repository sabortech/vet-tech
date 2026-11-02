query "veterinario/password" verb=POST {
  api_group = "Authentication"
  auth = "veterinario"
  input {
    text current_password
    text new_password
    text password_confirmation
  }
  stack {
    precondition ($input.current_password != "" && $input.new_password != "" && $input.password_confirmation != "") {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }
    precondition ($input.new_password == $input.password_confirmation) {
      error_type = "inputerror"
      error = "As senhas não coincidem."
    }
    db.get veterinario {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "senha"]
    } as $identity
    precondition ($identity != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    security.check_password {
      text_password = $input.current_password
      hash_password = $identity.senha
    } as $valid
    precondition ($valid) {
      error_type = "inputerror"
      error = "Senha atual incorreta."
    }
    db.edit veterinario {
      field_name = "id"
      field_value = $auth.id
      data = {senha: $input.new_password}
      output = ["id"]
    } as $updated
  }
  response = {success: true}
  tags = ["vettech"]
  guid = "zP_PWvABhW3pcqDUGRRO0afCgUA"
}
