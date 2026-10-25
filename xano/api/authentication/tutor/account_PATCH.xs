query "tutor/account" verb=PATCH {
  api_group = "Authentication"
  auth = "tutor"
  input {
    text nome filters=trim
    text telefone filters=trim
    text endereco filters=trim
  }
  stack {
    precondition ($input.nome != "" && $input.telefone != "" && $input.endereco != "") {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }
    db.get tutor {
      field_name = "id"
      field_value = $auth.id
      output = ["id"]
    } as $identity
    precondition ($identity != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    db.edit tutor {
      field_name = "id"
      field_value = $auth.id
      data = {nome: $input.nome, telefone: $input.telefone, endereco: $input.endereco}
      output = ["nome", "email", "cpf", "telefone", "endereco"]
    } as $account
    var $masked {
      value = "***.***.***-**"
    }
    conditional {
      if ("/^[0-9]{11}$/"|regex_matches:$account.cpf) {
        var.update $masked {
          value = "***."|concat:($account.cpf|substr:3:3)|concat:"."|concat:($account.cpf|substr:6:3)|concat:"-**"
        }
      }
    }
  }
  response = {
    nome: $account.nome
    email: $account.email
    cpf_mascarado: $masked
    telefone: $account.telefone
    endereco: $account.endereco
  }
  tags = ["vettech"]
  guid = "9VhEUxsiUl3NUsTndfdf-cVNwdw"
}
