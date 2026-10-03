query "tutor/login" verb=POST {
  api_group = "Authentication"

  input {
    email email filters=trim|lower
    text password
  }

  stack {
    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id", "password"]
    } as $tutor
  
    precondition ($tutor != null) {
      error_type = "accessdenied"
      error = "Credenciais inválidas."
    }
  
    security.check_password {
      text_password = $input.password
      hash_password = $tutor.password
    } as $password_valid
  
    precondition ($password_valid) {
      error_type = "accessdenied"
      error = "Credenciais inválidas."
    }
  
    security.create_auth_token {
      table = "tutor"
      extras = {}
      expiration = 86400
      id = $tutor.id
    } as $auth_token
  }

  response = {authToken: $auth_token, tutor_id: $tutor.id}
  guid = "he9cMOB7p42HYnPKHtdNiemr8Uk"
}