// Issues the same token as acesso/login (table, extras and expiration) for an
// identity already resolved by the backend. Never call with client input.
function "Identity/issue_session" {
  input {
    text perfil
    int identidade_id
  }

  stack {
    var $sessao {
      value = null
    }

    conditional {
      if ($input.perfil == "tutor") {
        security.create_auth_token {
          table = "tutor"
          extras = {perfil: "tutor"}
          expiration = 86400
          id = $input.identidade_id
        } as $token

        var.update $sessao {
          value = {
            authToken    : $token
            perfil       : "tutor"
            identidade_id: $input.identidade_id
          }
        }
      }

      elseif ($input.perfil == "veterinario") {
        security.create_auth_token {
          table = "veterinario"
          extras = {perfil: "veterinario"}
          expiration = 86400
          id = $input.identidade_id
        } as $token

        var.update $sessao {
          value = {
            authToken    : $token
            perfil       : "veterinario"
            identidade_id: $input.identidade_id
          }
        }
      }
    }

    precondition ($sessao != null) {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }
  }

  response = $sessao
  tags = ["vettech", "google-login"]
  guid = "5Pd2bdF6nwBFydy-MnLjTa_F-jc"
}
