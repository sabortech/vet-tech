// Um evento pode reservar no máximo uma tentativa, pelo índice único do banco.
function "Notifications/send_welcome_email" {
  input {int event_id}
  stack {
    function.run "Notifications/welcome_identity" {input={event_id:$input.event_id}
      mock = {"registra envio aceito": {"name": "Teste", "profile": "tutor", "recipient": "teste@example.invalid"}, "registra falha sem lancar erro": {"name": "Teste", "profile": "tutor", "recipient": "teste@example.invalid"}, "registra resultado incerto": {"name": "Teste", "profile": "tutor", "recipient": "teste@example.invalid"}}
    } as $person
    var $claimed {value=false}
    var $attempt {value=null}
    var $result {value={accepted:false, state:"ignorado"}}
    try_catch {
      try {
        db.add welcome_email_attempt {data={event_id:$input.event_id, state:"reservado"}
          mock = {"registra envio aceito": {"id": -1}, "registra falha sem lancar erro": {"id": -1}, "registra resultado incerto": {"id": -1}}
        } as $attempt
        var.update $claimed {value=true}
      }
      catch {
        var.update $claimed {value=false}
      }
    }
    conditional {
      if ($claimed) {
        var $receipt {value={accepted:false, state:"incerto", provider_id:""}}
        try_catch {
          try {
            function.run "Notifications/deliver_welcome_email" {
              input={recipient:$person.recipient, name:$person.name, profile:$person.profile}
              mock = {"registra envio aceito": {"accepted": true, "state": "aceito", "provider_id": "<simulado>"}, "registra falha sem lancar erro": {"accepted": false, "state": "falhou", "provider_id": ""}, "registra resultado incerto": {"accepted": false, "state": "incerto", "provider_id": ""}}
            } as $receipt
          }
          catch {
            var.update $receipt {value={accepted:false, state:"incerto", provider_id:""}}
          }
        }
        db.edit welcome_email_attempt {
          field_name="id"
          field_value=$attempt.id
          data={state:$receipt.state, provider_id:$receipt.provider_id, updated_at:now}
          mock = {"registra envio aceito": {"id": -1}, "registra falha sem lancar erro": {"id": -1}, "registra resultado incerto": {"id": -1}}
        } as $marked
        var.update $result {value={accepted:$receipt.accepted, state:$receipt.state}}
      }
    }
  }
  response=$result
  history=false
  tags=["vettech", "welcome-email"]
  test "registra envio aceito" {
    input = {"event_id": -1}
    expect.to_equal ($response.accepted) {value = true}
    expect.to_equal ($response.state) {value = "aceito"}
  }
  test "registra falha sem lancar erro" {
    input = {"event_id": -1}
    expect.to_equal ($response.accepted) {value = false}
    expect.to_equal ($response.state) {value = "falhou"}
  }
  test "registra resultado incerto" {
    input = {"event_id": -1}
    expect.to_equal ($response.accepted) {value = false}
    expect.to_equal ($response.state) {value = "incerto"}
  }

}
