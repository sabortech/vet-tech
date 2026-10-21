// Checks each domain credential independently; a shared email grants no role.
query "profiles/login" verb=POST {
  api_group = "Authentication"
  input {
    email email filters=trim|lower
    text password
  }
  stack {
    var $profiles {
      value = []
    }
    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id", "password"]
    } as $tutor
    conditional {
      if ($tutor != null) {
        security.check_password {
          text_password = $input.password
          hash_password = $tutor.password
        } as $tutor_valid
        conditional {
          if ($tutor_valid) {
            security.create_auth_token {
              table = "tutor"
              id = $tutor.id
              extras = {}
              expiration = 86400
            } as $tutor_token
            var.update $profiles {
              value = $profiles|push:{perfil: "tutor", id: $tutor.id, authToken: $tutor_token}
            }
          }
        }
      }
    }
    db.get veterinario {
      field_name = "email"
      field_value = $input.email
      output = ["id", "senha"]
    } as $veterinario
    conditional {
      if ($veterinario != null && $veterinario.senha != null) {
        security.check_password {
          text_password = $input.password
          hash_password = $veterinario.senha
        } as $veterinario_valid
        conditional {
          if ($veterinario_valid) {
            security.create_auth_token {
              table = "veterinario"
              id = $veterinario.id
              extras = {}
              expiration = 86400
            } as $veterinario_token
            var.update $profiles {
              value = $profiles|push:{perfil: "veterinario", id: $veterinario.id, authToken: $veterinario_token}
            }
          }
        }
      }
    }
    precondition (($profiles|count) > 0) {
      error_type = "accessdenied"
      error = "Credenciais inválidas."
    }
  }
  response = {profiles: $profiles}
}
