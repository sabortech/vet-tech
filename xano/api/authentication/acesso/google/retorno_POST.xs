// Finishes Google login. The state is consumed (single-use marker) before the
// code exchange. Linked sub: same session as acesso/login. Unlinked sub with
// one coherent identity and verified e-mail: linked automatically, same
// session, never asks for the Vet Tech password. Google tokens are never
// stored or returned.
query "acesso/google/retorno" verb=POST {
  api_group = "Authentication"

  input {
    text code filters=trim|max:2048 {
      sensitive = true
    }

    text state filters=trim|max:256 {
      sensitive = true
    }
  }

  stack {
    precondition ($input.code != "" && $input.state != "") {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }

    db.get tentativa_oauth_google {
      field_name = "state_hash"
      field_value = $input.state|sha256
      output = ["id", "code_verifier", "expira_em"]
    } as $tentativa

    precondition ($tentativa != null && $tentativa.expira_em > now) {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }

    // Unique insert: only the first request with this state gets through.
    var $consumido {
      value = false
    }

    try_catch {
      try {
        db.add uso_oauth_google {
          data = {chave: "state:" ~ ($tentativa.id|to_text)}
        } as $marcador

        var.update $consumido {
          value = true
        }
      }

      catch {
        var.update $consumido {
          value = false
        }
      }
    }

    precondition ($consumido) {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }

    db.del tentativa_oauth_google {
      field_name = "id"
      field_value = $tentativa.id
    }

    var $token_result {
      value = null
    }

    try_catch {
      try {
        api.request {
          url = "https://oauth2.googleapis.com/token"
          method = "POST"
          params = {
            code         : $input.code
            client_id    : $env.GOOGLE_OAUTH_CLIENT_ID
            client_secret: $env.GOOGLE_OAUTH_CLIENT_SECRET
            redirect_uri : $env.GOOGLE_OAUTH_REDIRECT_URI
            grant_type   : "authorization_code"
            code_verifier: $tentativa.code_verifier
          }
          headers = ["Content-Type: application/x-www-form-urlencoded"]
          timeout = 15
        } as $google

        conditional {
          if ($google.response.status == 200) {
            var.update $token_result {
              value = $google.response.result
            }
          }
        }
      }

      catch {
        var.update $token_result {
          value = null
        }
      }
    }

    precondition ($token_result != null && ($token_result|get:"id_token":"") != "") {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }

    // id_token received directly from Google over TLS with the client secret
    // (OIDC Core 3.1.3.7): claims are validated, signature check not required.
    var $partes {
      value = $token_result.id_token|split:"."
    }

    precondition (($partes|count) == 3) {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }

    var $claims {
      value = ($partes|get:1)|base64_decode_urlsafe|json_decode
    }

    var $issuer {
      value = $claims|get:"iss":""
    }

    precondition ($claims != null && ($issuer == "https://accounts.google.com" || $issuer == "accounts.google.com") && ($claims|get:"aud":"") == $env.GOOGLE_OAUTH_CLIENT_ID && (($claims|get:"exp":0)|to_int) * 1000 > now && ($claims|get:"sub":"") != "") {
      error_type = "accessdenied"
      error = "Não foi possível entrar com o Google. Tente novamente."
    }

    var $google_sub {
      value = $claims.sub|to_text
    }

    var $email_verificado {
      value = ($claims|get:"email_verified":false) == true || ($claims|get:"email_verified":"") == "true"
    }

    var $google_email {
      value = ($claims|get:"email":"")|to_text|trim|to_lower
    }

    db.get vinculo_google {
      field_name = "google_sub"
      field_value = $google_sub
      output = ["id", "perfil", "identidade_id"]
    } as $vinculo

    var $resposta {
      value = null
    }

    conditional {
      if ($vinculo != null) {
        function.run "Identity/linked_identity_valid" {
          input = {perfil: $vinculo.perfil, identidade_id: $vinculo.identidade_id}
        } as $vinculo_valido

        precondition ($vinculo_valido) {
          error_type = "accessdenied"
          error = "Não foi possível entrar com o Google. Tente novamente."
        }

        db.edit vinculo_google {
          field_name = "id"
          field_value = $vinculo.id
          data = {ultimo_uso_em: now}
        } as $vinculo_atualizado

        function.run "Identity/issue_session" {
          input = {perfil: $vinculo.perfil, identidade_id: $vinculo.identidade_id}
        } as $sessao

        var.update $resposta {
          value = {
            resultado    : "sessao"
            authToken    : $sessao.authToken
            perfil       : $sessao.perfil
            identidade_id: $sessao.identidade_id
          }
        }
      }

      else {
        precondition ($email_verificado && $google_email != "") {
          error_type = "accessdenied"
          error = "Não foi possível entrar com o Google. Tente novamente."
        }

        function.run "Identity/resolve_login_email" {
          input = {email: $google_email}
        } as $identidade

        precondition ($identidade.situacao != "sem_conta") {
          error_type = "accessdenied"
          error = "Não encontramos uma conta Vet Tech para esta conta Google. Faça seu cadastro ou entre com e-mail e senha."
        }

        precondition ($identidade.situacao == "ok") {
          error_type = "accessdenied"
          error = "Não foi possível entrar com o Google. Tente novamente."
        }

        db.query vinculo_google {
          where = $db.vinculo_google.perfil == $identidade.perfil && $db.vinculo_google.identidade_id == $identidade.identidade_id
          return = {type: "exists"}
        } as $identidade_ja_vinculada

        precondition ($identidade_ja_vinculada == false) {
          error_type = "accessdenied"
          error = "Não foi possível entrar com o Google. Tente novamente."
        }

        // First access: link automatically by verified e-mail, no password.
        // Unique indexes on sub and on (perfil, identidade_id) arbitrate races.
        var $vinculado {
          value = false
        }

        try_catch {
          try {
            db.add vinculo_google {
              data = {
                google_sub      : $google_sub
                perfil          : $identidade.perfil
                identidade_id   : $identidade.identidade_id
                email_no_vinculo: $google_email
                ultimo_uso_em   : now
              }
            } as $novo_vinculo

            var.update $vinculado {
              value = true
            }
          }

          catch {
            var.update $vinculado {
              value = false
            }
          }
        }

        precondition ($vinculado) {
          error_type = "accessdenied"
          error = "Não foi possível entrar com o Google. Tente novamente."
        }

        function.run "Identity/issue_session" {
          input = {perfil: $identidade.perfil, identidade_id: $identidade.identidade_id}
        } as $sessao_nova

        var.update $resposta {
          value = {
            resultado    : "sessao"
            authToken    : $sessao_nova.authToken
            perfil       : $sessao_nova.perfil
            identidade_id: $sessao_nova.identidade_id
          }
        }
      }
    }
  }

  response = $resposta
  tags = ["vettech", "google-login"]
  guid = "XeiVEQOw08_KKoVIxZjTORVZGqQ"
}
