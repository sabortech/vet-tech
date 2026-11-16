query "acesso/password-reset/verify" verb=POST {
  api_group = "Authentication"
  input {
    text challenge_id
    text code
  }
  stack {
    function.run "Security/password_operation" {
      input = {action: "verify", purpose: "reset", challenge_id: $input.challenge_id, code: $input.code}
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
