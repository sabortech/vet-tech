query "veterinario/account" verb=GET {
  api_group = "Authentication"
  auth = "veterinario"
  input {
  }
  stack {
    db.get veterinario {
      field_name = "id"
      field_value = $auth.id
      output = ["nome", "email", "telefone", "crmv", "crmv_uf", "cmv"]
    } as $account
    precondition ($account != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
  }
  response = {
    nome: $account.nome|first_notempty:""
    email: $account.email|first_notempty:""
    telefone: $account.telefone|first_notempty:""
    crmv: $account.crmv|first_notempty:$account.cmv|first_notempty:""
    crmv_uf: $account.crmv_uf|first_notempty:""
  }
  tags = ["vettech"]
  guid = "mAxakl9pRcaBREdIYXTE5Cc8KeM"
}
