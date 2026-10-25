query "tutor/password" verb=POST {
  api_group = "Authentication"
  auth = "tutor"
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
    db.get tutor {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "password"]
    } as $identity
    precondition ($identity != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    security.check_password {
      text_password = $input.current_password
      hash_password = $identity.password
    } as $valid
    precondition ($valid) {
      error_type = "inputerror"
      error = "Senha atual incorreta."
    }
    db.edit tutor {
      field_name = "id"
      field_value = $auth.id
      data = {password: $input.new_password}
      output = ["id"]
    } as $updated
  }
  response = {success: true}
  tags = ["vettech"]
  guid = "pR-EMDCqMBuRsE-RuFMb4Ua7BWo"
}
