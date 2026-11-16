// Starts Google login (OIDC authorization code + PKCE S256). The state is
// stored only as a hash, expires in 10 minutes and the redirect_uri comes
// from the environment, never from the client. Returns only the URL.
query "acesso/google/inicio" verb=GET {
  api_group = "Authentication"
  input {
    text intencao?="login"
  }

  stack {
    precondition ($input.intencao == "login" || $input.intencao == "cadastro") {
      error_type="inputerror"
      error="Operação inválida."
    }
    precondition ($env.GOOGLE_OAUTH_CLIENT_ID != null && $env.GOOGLE_OAUTH_CLIENT_ID != "" && $env.GOOGLE_OAUTH_CLIENT_SECRET != null && $env.GOOGLE_OAUTH_CLIENT_SECRET != "" && $env.GOOGLE_OAUTH_REDIRECT_URI != null && $env.GOOGLE_OAUTH_REDIRECT_URI != "") {
      error_type = "standard"
      error = "Login com Google indisponível no momento."
    }

    security.random_bytes {
      length = 32
    } as $state_bytes

    security.random_bytes {
      length = 48
    } as $verifier_bytes

    var $state {
      value = $state_bytes|base64_encode_urlsafe|replace:"=":""|replace:".":""
    }

    var $code_verifier {
      value = $verifier_bytes|base64_encode_urlsafe|replace:"=":""|replace:".":""
    }

    var $code_challenge {
      value = $code_verifier|sha256:true|base64_encode_urlsafe|replace:"=":""|replace:".":""
    }

    db.add tentativa_oauth_google {
      data = {
        intencao     : $input.intencao
        state_hash   : $state|sha256
        code_verifier: $code_verifier
        expira_em    : now|add_secs_to_timestamp:600
      }
    } as $tentativa

    var $url {
      value = "https://accounts.google.com/o/oauth2/v2/auth"
        |url_addarg:"client_id":$env.GOOGLE_OAUTH_CLIENT_ID
        |url_addarg:"redirect_uri":$env.GOOGLE_OAUTH_REDIRECT_URI
        |url_addarg:"response_type":"code"
        |url_addarg:"scope":"openid email profile"
        |url_addarg:"state":$state
        |url_addarg:"code_challenge":$code_challenge
        |url_addarg:"code_challenge_method":"S256"
        |url_addarg:"prompt":"select_account"
    }
  }

  response = {url: $url}
  tags = ["vettech", "google-login"]
  guid = "UHM-9AE2KMDA3hYhxmHiBgzJbfU"
}
