// Chamada interna; nunca expor como endpoint público de envio arbitrário.
function "Notifications/deliver_welcome_email" {
  input {
    email recipient
    text profile
    text name
  }
  stack {
    // .invalid é reservado para testes e nunca pode receber e-mail real.
    precondition (("/[.]invalid$/"|regex_matches:$input.recipient) == false) {
      error_type = "inputerror"
      error = "Destinatário inválido."
    }
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
    function.run "Notifications/render_welcome_email" {
      input = {profile: $input.profile, name: $input.name}
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
      mock = {"aceita entrega confirmada": {"response": {"status": 201, "result": {"messageId": "<simulado>"}}}, "recusa autenticacao": {"response": {"status": 401, "result": {}}}, "recusa cota": {"response": {"status": 429, "result": {}}}, "trata erro do provedor como incerto": {"response": {"status": 500, "result": {}}}, "nao aceita resposta sem identificador": {"response": {"status": 201, "result": {}}}}
    } as $delivery
    api.lambda {
      code = "const r=$var.delivery.response;const v=r.result||{};const accepted=r.status>=200&&r.status<300&&typeof v.messageId==='string'&&v.messageId.length>0;return {accepted,state:accepted?'aceito':(r.status>=400&&r.status<500?'falhou':'incerto'),provider_id:accepted?v.messageId:''};"
    } as $receipt
  }
  response = $receipt
  history = false
  tags = ["vettech", "welcome-email"]
  test "aceita entrega confirmada" {
    input = {"name": "Teste", "profile": "tutor", "recipient": "preview@example.com"}
    expect.to_equal ($response.accepted) {value = true}
    expect.to_equal ($response.state) {value = "aceito"}
  }
  test "recusa autenticacao" {
    input = {"name": "Teste", "profile": "tutor", "recipient": "preview@example.com"}
    expect.to_equal ($response.accepted) {value = false}
    expect.to_equal ($response.state) {value = "falhou"}
  }
  test "recusa cota" {
    input = {"name": "Teste", "profile": "tutor", "recipient": "preview@example.com"}
    expect.to_equal ($response.accepted) {value = false}
    expect.to_equal ($response.state) {value = "falhou"}
  }
  test "trata erro do provedor como incerto" {
    input = {"name": "Teste", "profile": "tutor", "recipient": "preview@example.com"}
    expect.to_equal ($response.accepted) {value = false}
    expect.to_equal ($response.state) {value = "incerto"}
  }
  test "nao aceita resposta sem identificador" {
    input = {"name": "Teste", "profile": "tutor", "recipient": "preview@example.com"}
    expect.to_equal ($response.accepted) {value = false}
    expect.to_equal ($response.state) {value = "incerto"}
  }

}
