query "veterinario/password" verb=POST {
  api_group = "Authentication"
  auth = "veterinario"
  input {
    text current_password
    text new_password
    text password_confirmation
    text challenge_id
    text code
  }
  stack {
    function.run "Security/password_operation" {
      input = {action: "change", purpose: "change", profile: "veterinario", actor_id: $auth.id, current_password: $input.current_password, new_password: $input.new_password, password_confirmation: $input.password_confirmation, challenge_id: $input.challenge_id, code: $input.code}
    } as $operation
    precondition ($operation.public.ok) {
      error_type = "inputerror"
      error = $operation.public.message
    }
  }
  response = $operation.public
  history = false
  tags = ["vettech", "password-security"]
  guid = "zP_PWvABhW3pcqDUGRRO0afCgUA"
}
