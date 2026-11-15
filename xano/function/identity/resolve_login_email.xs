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
    } as $tutor

    db.get veterinario {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $vet

    db.get reserva_email {
      field_name = "email"
      field_value = $input.email
      output = ["id", "perfil", "identidade_id"]
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
}
