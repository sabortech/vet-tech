query "acesso/google/cadastro" verb=POST {
  api_group="Authentication"
  input {
    text prova {sensitive=true}
    text perfil
    text nome filters=trim
    text telefone filters=trim
    text cpf?=""
    text endereco?=""
    text crmv?="" filters=trim|upper
    text crmv_uf?="" filters=trim|upper
    int clinica_id?
    int[] especies_ids?
    int[] especialidades_ids?
  }
  stack {
    db.get cadastro_google {
      field_name="prova_hash"
      field_value=$input.prova|sha256
      output=["id","google_sub","email","expira_em"]
    } as $proof
    precondition ($proof != null && $proof.expira_em > now && ($input.perfil == "tutor" || $input.perfil == "veterinario")) {
      error_type="accessdenied"
      error="Cadastro Google expirado ou inválido. Comece novamente."
    }
    var $created {value=null}
    db.transaction {
      stack {
        db.add uso_oauth_google {data={chave:"cadastro:" ~ ($proof.id|to_text)}} as $consumed
        conditional {
          if ($input.perfil == "tutor") {
            function.run "Identity/create_tutor" {
              input={nome:$input.nome,email:$proof.email,telefone:$input.telefone,cpf:$input.cpf,endereco:$input.endereco}
            } as $account
            var.update $created {value=$account}
          }
          else {
            function.run "Identity/create_veterinario" {
              input={nome:$input.nome,email:$proof.email,telefone:$input.telefone,crmv:$input.crmv,crmv_uf:$input.crmv_uf,clinica_id:$input.clinica_id,especies_ids:$input.especies_ids,especialidades_ids:$input.especialidades_ids}
            } as $account
            var.update $created {value=$account}
          }
        }
        db.add vinculo_google {
          data={google_sub:$proof.google_sub,perfil:$input.perfil,identidade_id:$created.identidade_id,email_no_vinculo:$proof.email,ultimo_uso_em:now}
        } as $link
      }
    }
    function.run "Identity/issue_session" {input={perfil:$input.perfil,identidade_id:$created.identidade_id}} as $session
    util.post_process {
      stack {
        try_catch {
          try {
            function.run "Notifications/send_welcome_email" {input={event_id:$created.event_id}} as $sent
          }
          catch {
            var $failed {value=true}
          }
        }
      }
    }
  }
  response={resultado:"sessao",authToken:$session.authToken,perfil:$session.perfil,identidade_id:$session.identidade_id}
  history=false
}
