// Same identity rules as acesso/login, without the password: exactly one
// identity between tutor and veterinario, with a coherent reserva_email.
// situacao: "ok" | "sem_conta" | "conflito". Internal use only.
function "Identity/resolve_login_email" {
  input {
    email email filters=trim|lower
  }

  stack {
    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
      mock = {
        "tutor unico com reserva coerente": {id: 7}
        "veterinario unico com reserva coerente": null
        "sem conta em nenhum perfil": null
        "email nos dois perfis": {id: 7}
        "reserva divergente da identidade": {id: 7}
        "reserva ausente": {id: 7}
      }
    } as $tutor

    db.get veterinario {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
      mock = {
        "tutor unico com reserva coerente": null
        "veterinario unico com reserva coerente": {id: 9}
        "sem conta em nenhum perfil": null
        "email nos dois perfis": {id: 9}
        "reserva divergente da identidade": null
        "reserva ausente": null
      }
    } as $vet

    db.get reserva_email {
      field_name = "email"
      field_value = $input.email
      output = ["id", "perfil", "identidade_id"]
      mock = {
        "tutor unico com reserva coerente": {id: -1, perfil: "tutor", identidade_id: 7}
        "veterinario unico com reserva coerente": {id: -1, perfil: "veterinario", identidade_id: 9}
        "sem conta em nenhum perfil": null
        "email nos dois perfis": {id: -1, perfil: "tutor", identidade_id: 7}
        "reserva divergente da identidade": {id: -1, perfil: "veterinario", identidade_id: 7}
        "reserva ausente": null
      }
    } as $reservation

    var $resultado {
      value = {situacao: "conflito", perfil: "", identidade_id: 0}
    }

    conditional {
      if ($tutor == null && $vet == null) {
        var.update $resultado {
          value = {situacao: "sem_conta", perfil: "", identidade_id: 0}
        }
      }

      elseif ($tutor != null && $vet == null && $reservation != null && $reservation.perfil == "tutor" && $reservation.identidade_id == $tutor.id) {
        var.update $resultado {
          value = {situacao: "ok", perfil: "tutor", identidade_id: $tutor.id}
        }
      }

      elseif ($tutor == null && $vet != null && $reservation != null && $reservation.perfil == "veterinario" && $reservation.identidade_id == $vet.id) {
        var.update $resultado {
          value = {situacao: "ok", perfil: "veterinario", identidade_id: $vet.id}
        }
      }
    }
  }

  response = $resultado
  tags = ["vettech", "google-login"]
  guid = "FhsegRoN10Qt-rwdbd1MqDLuoAw"

  test "tutor unico com reserva coerente" {
    input = {email: "teste@example.invalid"}
    expect.to_equal ($response.situacao) {
      value = "ok"
    }

    expect.to_equal ($response.perfil) {
      value = "tutor"
    }
  }

  test "veterinario unico com reserva coerente" {
    input = {email: "teste@example.invalid"}
    expect.to_equal ($response.situacao) {
      value = "ok"
    }

    expect.to_equal ($response.perfil) {
      value = "veterinario"
    }
  }

  test "sem conta em nenhum perfil" {
    input = {email: "teste@example.invalid"}
    expect.to_equal ($response.situacao) {
      value = "sem_conta"
    }
  }

  test "email nos dois perfis" {
    input = {email: "teste@example.invalid"}
    expect.to_equal ($response.situacao) {
      value = "conflito"
    }
  }

  test "reserva divergente da identidade" {
    input = {email: "teste@example.invalid"}
    expect.to_equal ($response.situacao) {
      value = "conflito"
    }
  }

  test "reserva ausente" {
    input = {email: "teste@example.invalid"}
    expect.to_equal ($response.situacao) {
      value = "conflito"
    }
  }
}
