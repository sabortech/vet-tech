// Internal only. Domain identity arguments are supplied exclusively by API wrappers.
function "Security/password_operation" {
  input {
    text action
    text purpose
    text profile?=""
    int actor_id?=0
    email email? filters=trim|lower
    text challenge_id?=""
    text code?=""
    text reset_token?=""
    text current_password?=""
    text new_password?=""
    text password_confirmation?=""
    bool delivered?=false
  }
  stack {
    api.lambda {
      code = """
        if(typeof $env.PASSWORD_CODE_SECRET!=='string'||$env.PASSWORD_CODE_SECRET.length<32)throw Error('Serviço de verificação indisponível.');
        if(!['request','verify','complete','change','delivery'].includes($input.action)||!['change','reset'].includes($input.purpose))throw Error('Operação inválida.');
        if(['verify','complete'].includes($input.action)&&$input.purpose!=='reset')throw Error('Operação inválida.');
        return {authenticated:['tutor','veterinario'].includes($input.profile)&&$input.actor_id>0};
        """
    } as $context
    precondition ($input.purpose != "change" || $context.authenticated || $input.action == "delivery") {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    security.random_bytes {
      length = 32
    } as $nonce
    var.update $nonce { value = $nonce|base64_encode }
    security.random_bytes {
      length = 32
    } as $grant_nonce
    var.update $grant_nonce { value = $grant_nonce|base64_encode }
    security.random_number {
      min = 0
      max = 999999
    } as $number
    var $public_id { value = $nonce }
    var $grant_token { value = $grant_nonce }
    var $grant_digest { value = $grant_token|hmac_sha256:$env.PASSWORD_CODE_SECRET }
    var $presented_token { value = "" }
    var $presented_code { value = "" }
    conditional {
      if ($input.reset_token != null) {
        var.update $presented_token { value = $input.reset_token }
      }
    }
    conditional {
      if ($input.code != null) {
        var.update $presented_code { value = $input.code }
      }
    }
    var $presented_grant_digest { value = $presented_token|hmac_sha256:$env.PASSWORD_CODE_SECRET }
    api.lambda {
      code = "return String($var.number).padStart(6,'0');"
    } as $generated_code
    var $generated_material { value = $public_id ~ ":" ~ $generated_code }
    var $generated_digest { value = $generated_material|hmac_sha256:$env.PASSWORD_CODE_SECRET }
    var $origin_key { value = $env.$remote_ip|hmac_sha256:$env.PASSWORD_CODE_SECRET }
    var $result { value = null }
    db.transaction {
      stack {
        db.add password_lock { data = {key: "password-security"} } as $guard
        var $row { value = null }
        var $person { value = null }
        var $identity_profile { value = $input.profile }
        conditional {
          if ($input.action != "request") {
            conditional {
              if ($input.action == "complete") {
                db.get password_challenge { field_name = "grant_digest"
                  field_value = $presented_grant_digest
                } as $row
              }
              else {
                db.get password_challenge { field_name = "public_id"
                  field_value = $input.challenge_id
                } as $row
              }
            }
            conditional {
              if ($row != null && !$context.authenticated) {
                var.update $identity_profile { value = $row.profile }
              }
            }
          }
        }
        conditional {
          if ($context.authenticated) {
            conditional {
              if ($input.profile == "tutor") {
                db.get tutor { field_name = "id"
                  field_value = $input.actor_id
                  output = ["id", "email", "password"]
                } as $person
              }
              else {
                db.get veterinario { field_name = "id"
                  field_value = $input.actor_id
                  output = ["id", "email", "senha"]
                } as $person
              }
            }
          }
          elseif ($input.action == "request") {
            db.get tutor { field_name = "email"
              field_value = $input.email
              output = ["id", "email", "password"]
            } as $tutor
            db.get veterinario { field_name = "email"
              field_value = $input.email
              output = ["id", "email", "senha"]
            } as $vet
            db.get reserva_email { field_name = "email"
              field_value = $input.email
              output = ["id", "perfil", "identidade_id"]
            } as $reservation
            conditional {
              if ($tutor != null && $vet == null && $reservation.perfil == "tutor" && $reservation.identidade_id == $tutor.id) {
                var.update $person { value = $tutor }
                var.update $identity_profile { value = "tutor" }
              }
              elseif ($vet != null && $tutor == null && $reservation.perfil == "veterinario" && $reservation.identidade_id == $vet.id) {
                var.update $person { value = $vet }
                var.update $identity_profile { value = "veterinario" }
              }
            }
          }
          elseif ($row != null) {
            conditional {
              if ($row.profile == "tutor") {
                db.get tutor { field_name = "id"
                  field_value = $row.identity_id
                  output = ["id", "email", "password"]
                } as $person
              }
              elseif ($row.profile == "veterinario") {
                db.get veterinario { field_name = "id"
                  field_value = $row.identity_id
                  output = ["id", "email", "senha"]
                } as $person
              }
            }
          }
        }
        precondition (!$context.authenticated || $person != null) {
          error_type = "accessdenied"
          error = "Sessão inválida."
        }
        var $account_email { value = "" }
        conditional {
          if ($input.email != null) {
            var.update $account_email { value = $input.email }
          }
        }
        var $credential { value = "" }
        var $resolved_id { value = 0 }
        conditional {
          if ($person != null) {
            var.update $resolved_id { value = $person.id }
            var.update $account_email { value = $person.email }
            conditional {
              if ($identity_profile == "tutor") {
                var.update $credential { value = $person.password }
              }
              else {
                var.update $credential { value = $person.senha }
              }
            }
          }
        }
        var $account_material { value = ($account_email|trim|to_lower) ~ ":" ~ $input.purpose }
        var $account_key { value = $account_material|hmac_sha256:$env.PASSWORD_CODE_SECRET }
        conditional {
          if ($input.action != "request" && $row != null) {
            var.update $account_key { value = $row.key }
          }
        }
        conditional {
          if ($credential == null || $credential == "") {
            var.update $credential {value="google-without-local-password"}
          }
        }
        var $fingerprint { value = $credential|hmac_sha256:$env.PASSWORD_CODE_SECRET }
        var $current_valid { value = false }
        conditional {
          if ($context.authenticated && $credential != "google-without-local-password" && ($input.action == "request" || $input.action == "change")) {
            security.check_password {
              text_password = $input.current_password
              hash_password = $credential
            } as $current_valid
          }
        }
        conditional {
          if ($input.action == "request") {
            db.get password_challenge { field_name = "key"
              field_value = $account_key
            } as $row
          }
        }
        var $origin { value = null }
        db.get password_origin { field_name = "key"
          field_value = $origin_key
        } as $origin
        var $row_public_id { value = "" }
        conditional {
          if ($row != null) {
            var.update $row_public_id { value = $row.public_id }
          }
        }
        var $presented_material { value = $row_public_id ~ ":" ~ $presented_code }
        var $presented_digest { value = $presented_material|hmac_sha256:$env.PASSWORD_CODE_SECRET }
        var $origin_times { value = [] }
        conditional {
          if ($origin != null) {
            var.update $origin_times { value = $origin.times }
          }
        }
        var $operation_context {
          value = {payload: {action: $input.action, purpose: $input.purpose, profile: $input.profile, actor_id: $input.actor_id, code: $presented_code, new_password: $input.new_password, password_confirmation: $input.password_confirmation}, row: $row, person: $person, fingerprint: $fingerprint, current_valid: $current_valid, authenticated: $context.authenticated, delivered: $input.delivered, origin_times: $origin_times, presented_code_digest: $presented_digest, presented_grant_digest: $presented_grant_digest, generated: {public_id: $public_id, code_digest: $generated_digest, grant_token: $grant_token, grant_digest: $grant_digest}}
        }
        api.lambda {
          code = """
// POLICY_BEGIN
// Pure decision logic, embedded in Security/password_operation by the generator.
// Cryptography, identity, persistence and transaction boundaries belong to Xano.
function decidePasswordOperation(c) {
  const now=c.now, p=c.payload, row=c.row;
  const state=JSON.parse(JSON.stringify(row?.state||{}));
  state.sends=(state.sends||[]).filter(t=>t>now-3600000);
  const origin=(c.origin_times||[]).filter(t=>t>now-3600000);
  let reply={ok:false,message:'Código inválido ou expirado. Solicite um novo código.'};
  const out={state,origin,reply,write_password:false,send:false,skip:false,event:'rejected',public_id:row?.public_id||'',grant_digest:row?.grant_digest||''};
  const equal=(a,b)=>{if(typeof a!=='string'||typeof b!=='string'||a.length!==b.length)return false;let diff=0;for(let i=0;i<a.length;i++)diff|=a.charCodeAt(i)^b.charCodeAt(i);return diff===0;};
  const credentialOK=!!c.person&&equal(state.fingerprint,c.fingerprint);
  if(p.action==='request') {
    const publicReply={ok:true,challenge_id:c.generated.public_id,expires_in:600,retry_after:60,message:'Se houver uma conta para este e-mail, enviaremos um código.'};
    out.reply=publicReply;
    const originLimited=origin.length>=20;
    if(!originLimited)origin.push(now);
    const limited=originLimited||state.sends.length>=5||state.sends.some(t=>t>now-60000);
    if(c.authenticated&&!c.current_valid){out.reply={ok:false,message:'Senha atual incorreta.'};return out;}
    if(limited){if(c.authenticated)out.reply={ok:false,message:'Aguarde antes de solicitar outro código.'};return out;}
    state.sends.push(now);
    out.public_id=c.generated.public_id;out.grant_digest='';
    state.challenge={digest:c.generated.code_digest,expires:now+600000,attempts:0,sent:false,consumed:false};
    state.grant=null;state.fingerprint=c.fingerprint;
    out.send=!!c.person;out.event='requested';return out;
  }
  const challenge=state.challenge;
  if(p.action==='delivery') {
    if(challenge&&!challenge.consumed&&challenge.expires>now){challenge.sent=c.delivered===true;out.event=c.delivered?'accepted':'delivery_failed';}
    out.reply={ok:true};return out;
  }
  if(p.action==='complete') {
    if(!credentialOK||!state.grant||state.grant.expires<=now||state.grant.consumed||!equal(out.grant_digest,c.presented_grant_digest))return out;
    if(!p.new_password||p.new_password!==p.password_confirmation){out.reply={ok:false,message:'As senhas não coincidem.'};return out;}
    state.grant.consumed=true;challenge.consumed=true;out.grant_digest='';out.write_password=true;
  } else if(p.action==='verify'||p.action==='change') {
    if(p.action==='change'&&(!c.authenticated||!c.current_valid)){out.reply={ok:false,message:'Senha atual incorreta.'};return out;}
    if(!credentialOK||!challenge||!challenge.sent||challenge.consumed||challenge.expires<=now||challenge.attempts>=5)return out;
    if(!/^[0-9]{6}$/.test(p.code||'')||!equal(challenge.digest,c.presented_code_digest)){challenge.attempts++;return out;}
    if(p.action==='verify') {
      challenge.consumed=true;state.grant={expires:now+300000,consumed:false};out.grant_digest=c.generated.grant_digest;
      out.reply={ok:true,reset_token:c.generated.grant_token,expires_in:300};out.event='verified';return out;
    }
    if(!p.new_password||p.new_password!==p.password_confirmation){out.reply={ok:false,message:'As senhas não coincidem.'};return out;}
    challenge.consumed=true;state.grant=null;out.grant_digest='';out.write_password=true;
  }
  if(out.write_password){out.reply={ok:true,success:true};out.event='completed';}
  return out;
}
// POLICY_END
            const c=$var.operation_context;
            c.now=Date.now();
            const p=c.payload, row=c.row;
            const own=!c.authenticated||(row?.profile===p.profile&&row?.identity_id===p.actor_id);
            const scoped=row?.state?.purpose===p.purpose;
            c.row=own&&scoped?row:null;
            const result=decidePasswordOperation(c);
            result.state.purpose=p.purpose;
            if(p.action!=='request'&&(!own||!scoped)){result.reply={ok:false,message:'Código inválido ou expirado. Solicite um novo código.'};result.write_password=false;result.skip=true;}
            return result;
            """
        } as $decision
        conditional {
          if ($input.action == "request") {
            db.add_or_edit password_origin { field_name = "key"
              field_value = $origin_key
              data = {key: $origin_key, times: $decision.origin, updated_at: "now"}
            } as $rate_saved
          }
        }
        conditional {
          if ($decision.skip != true && ($row != null || $decision.event == "requested")) {
            db.add_or_edit password_challenge { field_name = "key"
              field_value = $account_key
              data = {key: $account_key, public_id: $decision.public_id, grant_digest: $decision.grant_digest, profile: $identity_profile, identity_id: $resolved_id, state: $decision.state, updated_at: "now"}
            } as $saved
          }
        }
        conditional {
          if ($decision.write_password) {
            conditional {
              if ($identity_profile == "tutor") {
                db.edit tutor { field_name = "id"
                  field_value = $person.id
                  data = {password: $input.new_password}
                  output = ["id"]
                } as $updated
              }
              else {
                db.edit veterinario { field_name = "id"
                  field_value = $person.id
                  data = {senha: $input.new_password}
                  output = ["id"]
                } as $updated
              }
            }
            db.query password_challenge {
              where = $db.password_challenge.profile == $identity_profile && $db.password_challenge.identity_id == $person.id
              return = {type: "list"}
            } as $pending
            foreach ($pending) {
              each as $pending_row {
                api.lambda {
                  code = "const s=$var.pending_row.state;if(s.challenge)s.challenge.consumed=true;if(s.grant)s.grant.consumed=true;return s;"
                } as $invalidated
                db.edit password_challenge { field_name = "id"
                  field_value = $pending_row.id
                  data = {state: $invalidated, grant_digest: ""}
                } as $invalidated_row
              }
            }
          }
        }
        db.add password_event {
          data = {profile: $identity_profile, identity_id: $resolved_id, purpose: $input.purpose, outcome: $decision.event}
        } as $event
        var.update $result {
          value = {public: $decision.reply, send: $decision.send, challenge_id: $decision.public_id, recipient: $account_email, code: $generated_code}
        }
        db.del password_lock { field_name = "id"
          field_value = $guard.id
        }
      }
    }
  }
  response = $result
  history = false
  tags = ["vettech", "password-security"]
}
