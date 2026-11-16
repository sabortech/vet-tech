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
