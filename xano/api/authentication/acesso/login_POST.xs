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

    db.get clinica_admin {
      field_name = "email"
      field_value = $input.email
      output = ["id", "senha", "ativo", "clinica_id"]
    } as $admin

    db.get reserva_email {
      field_name = "email"
      field_value = $input.email
      output = ["id", "perfil", "identidade_id"]
    } as $reservation

    precondition (($tutor != null && $vet == null && $admin == null) || ($tutor == null && $vet != null && $admin == null) || ($tutor == null && $vet == null && $admin != null)) {
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

        precondition ($tutor.password != null && $tutor.password != "") {
          error_type="accessdenied"
          error="Credenciais inválidas."
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

      elseif ($vet != null) {
        precondition ($reservation.perfil == "veterinario" && $reservation.identidade_id == $vet.id) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }

        precondition ($vet.senha != null && $vet.senha != "") {
          error_type="accessdenied"
          error="Credenciais inválidas."
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

      else {
        precondition ($admin.ativo == true && $admin.clinica_id != null && $reservation.perfil == "clinica" && $reservation.identidade_id == $admin.id) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }
        db.get clinica {
          field_name = "id"
          field_value = $admin.clinica_id
          output = ["id"]
        } as $clinica
        precondition ($clinica != null && $admin.senha != null && $admin.senha != "") {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }
        security.check_password {
          text_password = $input.password
          hash_password = $admin.senha
        } as $valid_admin
        precondition ($valid_admin) {
          error_type = "accessdenied"
          error = "Credenciais inválidas."
        }
        security.create_auth_token {
          table = "clinica_admin"
          extras = {perfil: "clinica"}
          expiration = 86400
          id = $admin.id
        } as $token_admin
        var.update $login_result {
          value = {authToken: $token_admin, perfil: "clinica", identidade_id: $admin.id}
        }
      }
    }
  }

  response = $login_result
  history = false
  tags = ["vettech"]
  guid = "VgaizmK8G72qk6sAb5Z_hYk3ta0"
}
