query "acesso/login" verb=POST {
  api_group = "Authentication"

  input {
    email email filters=trim|lower
    text password
  }

  stack {
    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id", "password"]
    } as $tutor

    db.get veterinario {
      field_name = "email"
      field_value = $input.email
      output = ["id", "senha"]
    } as $vet

    db.get reserva_email {
      field_name = "email"
      field_value = $input.email
      output = ["id", "perfil", "identidade_id"]
    } as $reservation

    precondition (($tutor != null && $vet == null) || ($tutor == null && $vet != null)) {
      error_type = "accessdenied"
      error = "Credenciais inválidas."
    }

    precondition ($reservation != null) {
      error_type = "accessdenied"
      error = "Credenciais inválidas."
    }

    var $login_result {
      value = {}
    }

    conditional {
      if ($tutor != null) {
        precondition ($reservation.perfil == "tutor" && $reservation.identidade_id == $tutor.id) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }

        security.check_password {
          text_password = $input.password
          hash_password = $tutor.password
        } as $valid

        precondition ($valid) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }

        security.create_auth_token {
          table = "tutor"
          extras = {perfil: "tutor"}
          expiration = 86400
          id = $tutor.id
        } as $token

        var.update $login_result {
          value = {
            authToken    : $token
            perfil       : "tutor"
            identidade_id: $tutor.id
          }
        }
      }

      else {
        precondition ($reservation.perfil == "veterinario" && $reservation.identidade_id == $vet.id) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }

        security.check_password {
          text_password = $input.password
          hash_password = $vet.senha
        } as $valid

        precondition ($valid) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }

        security.create_auth_token {
          table = "veterinario"
          extras = {perfil: "veterinario"}
          expiration = 86400
          id = $vet.id
        } as $token

        var.update $login_result {
          value = {
            authToken    : $token
            perfil       : "veterinario"
            identidade_id: $vet.id
          }
        }
      }
    }
  }

  response = $login_result
  tags = ["vettech"]
  guid = "VgaizmK8G72qk6sAb5Z_hYk3ta0"
}
