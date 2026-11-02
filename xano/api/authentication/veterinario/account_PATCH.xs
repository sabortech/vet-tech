query "veterinario/account" verb=PATCH {
  api_group = "Authentication"
  auth = "veterinario"
  input {
    text nome filters=trim
    text telefone filters=trim
  }
  stack {
    precondition ($input.nome != "" && $input.telefone != "") {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }
    db.get veterinario {
      field_name = "id"
      field_value = $auth.id
      output = ["id"]
    } as $identity
    precondition ($identity != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    db.edit veterinario {
      field_name = "id"
      field_value = $auth.id
      data = {nome: $input.nome, telefone: $input.telefone}
      output = ["nome", "email", "telefone", "crmv", "crmv_uf", "cmv"]
    } as $account
  }
  response = {
    nome: $account.nome|first_notempty:""
    email: $account.email|first_notempty:""
    telefone: $account.telefone|first_notempty:""
    crmv: $account.crmv|first_notempty:$account.cmv|first_notempty:""
    crmv_uf: $account.crmv_uf|first_notempty:""
  }
  tags = ["vettech"]
  guid = "aUG04naGxC-9a87ZOvzaH1kBc3U"
}
