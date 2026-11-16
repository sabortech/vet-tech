query "acesso/password-reset/request" verb=POST {
  api_group = "Authentication"
  input {
    email email filters=trim|lower
  }
  stack {
    function.run "Security/password_operation" {
      input = {action: "request", purpose: "reset", email: $input.email}
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
                  input = {recipient: $operation.recipient, purpose: "reset", code: $operation.code}
                } as $delivery
                var.update $accepted { value = $delivery.accepted }
              }
              catch {
                var.update $accepted { value = false }
              }
            }
            function.run "Security/password_operation" {
              input = {action: "delivery", purpose: "reset", challenge_id: $operation.challenge_id, delivered: $accepted}
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
