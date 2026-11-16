query "tutor/password/request-code" verb=POST {
  api_group = "Authentication"
  auth = "tutor"
  input {
    text current_password
  }
  stack {
    function.run "Security/password_operation" {
      input = {action: "request", purpose: "change", profile: "tutor", actor_id: $auth.id, current_password: $input.current_password}
    } as $operation
    precondition ($operation.public.ok) {
      error_type = "inputerror"
      error = $operation.public.message
    }

    util.post_process {
      stack {
        conditional {
          if ($operation.send) {
            var $accepted { value = false }
            try_catch {
              try {
                function.run "Security/send_password_email" {
                  input = {recipient: $operation.recipient, purpose: "change", code: $operation.code}
                } as $delivery
                var.update $accepted { value = $delivery.accepted }
              }
              catch {
                var.update $accepted { value = false }
              }
            }
            function.run "Security/password_operation" {
              input = {action: "delivery", purpose: "change", challenge_id: $operation.challenge_id, delivered: $accepted}
            } as $marked
          }
        }
      }
    }
  }
  response = $operation.public
  history = false
  tags = ["vettech", "password-security"]
}
