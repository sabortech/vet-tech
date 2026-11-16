// Resolve somente eventos de cadastro; nunca recebe destinatário livre.
function "Notifications/welcome_identity" {
  input { int event_id }
  stack {
    db.get welcome_email_event {field_name="id"
      field_value=$input.event_id
      mock = {"resolve tutor": {"id": 1, "profile": "tutor", "identity_id": 42}, "resolve veterinario com mesmo id": {"id": 2, "profile": "veterinario", "identity_id": 42}, "nega evento ausente": null, "nega perfil invalido": {"id": 3, "profile": "user", "identity_id": 42}, "nega reserva divergente": {"id": 4, "profile": "tutor", "identity_id": 42}}
    } as $event
    precondition ($event != null && ($event.profile == "tutor" || $event.profile == "veterinario") && $event.identity_id > 0) {
      error_type="inputerror"
      error="Evento de boas-vindas inválido."
    }
    var $person {value=null}
    conditional {
      if ($event.profile == "tutor") {
        db.get tutor {field_name="id"
      field_value=$event.identity_id
      output=["id", "nome", "email"]
          mock = {"resolve tutor": {"id": 42, "nome": "Tutor Teste", "email": "tutor@example.invalid"}, "resolve veterinario com mesmo id": {"id": 42, "nome": "Vet Teste", "email": "vet@example.invalid"}, "nega evento ausente": null, "nega perfil invalido": null, "nega reserva divergente": {"id": 42, "nome": "Tutor Teste", "email": "tutor@example.invalid"}}
        } as $person
      }
      else {
        db.get veterinario {field_name="id"
      field_value=$event.identity_id
      output=["id", "nome", "email"]
          mock = {"resolve tutor": {"id": 42, "nome": "Tutor Teste", "email": "tutor@example.invalid"}, "resolve veterinario com mesmo id": {"id": 42, "nome": "Vet Teste", "email": "vet@example.invalid"}, "nega evento ausente": null, "nega perfil invalido": null, "nega reserva divergente": {"id": 42, "nome": "Tutor Teste", "email": "tutor@example.invalid"}}
        } as $person
      }
    }
    precondition ($person != null && $person.email != null && $person.email != "" && $person.nome != null && $person.nome != "") {
      error_type="inputerror"
      error="Evento de boas-vindas inválido."
    }
    db.get reserva_email {field_name="email"
      field_value=$person.email
      output=["perfil", "identidade_id"]
      mock = {"resolve tutor": {"perfil": "tutor", "identidade_id": 42}, "resolve veterinario com mesmo id": {"perfil": "veterinario", "identidade_id": 42}, "nega evento ausente": null, "nega perfil invalido": null, "nega reserva divergente": {"perfil": "veterinario", "identidade_id": 42}}
    } as $reservation
    precondition ($reservation != null && $reservation.perfil == $event.profile && $reservation.identidade_id == $event.identity_id) {
      error_type="inputerror"
      error="Evento de boas-vindas inválido."
    }
  }
  response={name:$person.nome, recipient:$person.email, profile:$event.profile}
  history=false
  tags=["vettech", "welcome-email"]
  test "resolve tutor" {
    input = {"event_id": -1}
    expect.to_equal ($response.profile) {value = "tutor"}
    expect.to_equal ($response.recipient) {value = "tutor@example.invalid"}
  }
  test "resolve veterinario com mesmo id" {
    input = {"event_id": -1}
    expect.to_equal ($response.profile) {value = "veterinario"}
    expect.to_equal ($response.recipient) {value = "vet@example.invalid"}
  }
  test "nega evento ausente" {
    input = {"event_id": -1}
    expect.to_throw {exception = "Evento de boas-vindas inválido."}
  }
  test "nega perfil invalido" {
    input = {"event_id": -1}
    expect.to_throw {exception = "Evento de boas-vindas inválido."}
  }
  test "nega reserva divergente" {
    input = {"event_id": -1}
    expect.to_throw {exception = "Evento de boas-vindas inválido."}
  }

}
