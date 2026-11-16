// Exclusivo do backend local: assinatura com prazo curto; nunca chamar do navegador.
query "acesso/password-reset/cleanup" verb=POST {
  api_group = "Authentication"
  input {
    int timestamp
    text signature
  }
  stack {
    var $material { value = "password-cleanup:" ~ ($input.timestamp|to_text) }
    var $expected { value = $material|hmac_sha256:$env.PASSWORD_CODE_SECRET }
    api.lambda {
      code = """
        const a=$input.signature,b=$var.expected;
        if(typeof $env.PASSWORD_CODE_SECRET!=='string'||$env.PASSWORD_CODE_SECRET.length<32||!Number.isSafeInteger($input.timestamp)||Math.abs(Date.now()-$input.timestamp)>300000||typeof a!=='string'||typeof b!=='string'||a.length!==b.length)return false;
        let diff=0;for(let i=0;i<a.length;i++)diff|=a.charCodeAt(i)^b.charCodeAt(i);return diff===0;
        """
    } as $authorized
    precondition ($authorized) {
      error_type = "accessdenied"
      error = "Operação não autorizada."
    }
    api.lambda {
      code = "return {temporary:Date.now()-86400000,events:Date.now()-30*86400000};"
    } as $cutoff
    db.transaction {
      stack {
        db.add password_lock { data = {key: "password-security"} } as $guard
        db.bulk.delete password_challenge {
          where = $db.password_challenge.updated_at < $cutoff.temporary
        }
        db.bulk.delete password_origin {
          where = $db.password_origin.updated_at < $cutoff.temporary
        }
        db.bulk.delete password_event {
          where = $db.password_event.created_at < $cutoff.events
        }
        db.del password_lock { field_name = "id"
          field_value = $guard.id
        }
      }
    }
  }
  response = {success: true}
  history = false
  tags = ["vettech", "password-security"]
}
