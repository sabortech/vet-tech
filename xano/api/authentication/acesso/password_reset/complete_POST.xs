query "acesso/password-reset/complete" verb=POST {
  api_group = "Authentication"
  input {
    text reset_token
    text new_password
    text password_confirmation
  }
  stack {
    function.run "Security/password_operation" {
      input = {action: "complete", purpose: "reset", reset_token: $input.reset_token, new_password: $input.new_password, password_confirmation: $input.password_confirmation}
    } as $operation
    precondition ($operation.public.ok) {
      error_type = "inputerror"
      error = $operation.public.message
    }
  }
  response = $operation.public
  history = false
  tags = ["vettech", "password-security"]
}
