// Chamada interna; nunca expor como endpoint público de envio arbitrário.
function "Security/send_password_email" {
  input {
    email recipient
    text purpose
    text code
  }
  stack {
    precondition ($env.BREVOS_API != null && $env.BREVOS_API != "" && $env.PASSWORD_EMAIL_FROM != null && $env.PASSWORD_EMAIL_FROM != "") {
      error_type = "standard"
      error = "Serviço de e-mail indisponível."
    }
    api.lambda {
      code = "const raw=String($env.PASSWORD_EMAIL_FROM||'').trim();const match=raw.match(/^([^<>\\r\\n]+)<([^<>\\r\\n]+)>$/);const email=(match?match[2]:raw).trim();const name=match?match[1].trim():'Vet Tech';return {email,name,valid:!!name&&/^[^\\s<>@]+@[^\\s<>@]+\\.[^\\s<>@]+$/.test(email)};"
    } as $sender
    precondition ($sender.valid == true) {
      error_type = "standard"
      error = "Serviço de e-mail indisponível."
    }
    function.run "Security/render_password_email" {
      input = {purpose: $input.purpose, code: $input.code, validity_minutes: 10}
    } as $message
    // Referência independente por envio; não reutilizar código ou desafio.
    security.random_bytes {
      length = 16
    } as $message_reference
    var.update $message_reference { value = $message_reference|base64_encode }
    api.request {
      url = "https://api.brevo.com/v3/smtp/email"
      method = "POST"
      params = {sender: {name: $sender.name, email: $sender.email}, to: [{email: $input.recipient}], subject: $message.subject, htmlContent: $message.html, textContent: $message.text, headers: {"X-Entity-Ref-ID": $message_reference}}
      headers = ["Content-Type: application/json", "api-key: " ~ $env.BREVOS_API]
      timeout = 15
    } as $delivery
    precondition ($delivery.response.status >= 200 && $delivery.response.status < 300 && $delivery.response.result.messageId != null && $delivery.response.result.messageId != "") {
      error_type = "standard"
      error = "Serviço de e-mail indisponível."
    }
  }
  response = {accepted: true}
  history = false
  tags = ["vettech", "password-security"]
}
