// Confirms that a Google link still points to an existing identity whose
// e-mail resolves back to it through the same rules as acesso/login.
function "Identity/linked_identity_valid" {
  input {
    text perfil
    int identidade_id
  }

  stack {
    var $email {
      value = null
    }

    conditional {
      if ($input.perfil == "tutor") {
        db.get tutor {
          field_name = "id"
          field_value = $input.identidade_id
          output = ["id", "email"]
        } as $tutor

        conditional {
          if ($tutor != null) {
            var.update $email {
              value = $tutor.email
            }
          }
        }
      }

      elseif ($input.perfil == "veterinario") {
        db.get veterinario {
          field_name = "id"
          field_value = $input.identidade_id
          output = ["id", "email"]
        } as $vet

        conditional {
          if ($vet != null) {
            var.update $email {
              value = $vet.email
            }
          }
        }
      }
    }

    var $valido {
      value = false
    }

    conditional {
      if ($email != null && $email != "") {
        function.run "Identity/resolve_login_email" {
          input = {email: $email}
        } as $resolved

        var.update $valido {
          value = $resolved.situacao == "ok" && $resolved.perfil == $input.perfil && $resolved.identidade_id == $input.identidade_id
        }
      }
    }
  }

  response = $valido
  tags = ["vettech", "google-login"]
  guid = "zCvGa0dZOv3R-x4sj8kTOdC5V_g"
}
