query "tutor/account" verb=GET {
  api_group = "Authentication"
  auth = "tutor"
  input {
  }
  stack {
    db.get tutor {
      field_name = "id"
      field_value = $auth.id
      output = ["nome", "email", "cpf", "telefone", "endereco"]
    } as $account
    precondition ($account != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
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
  guid = "XJ4mVXyQ6y_0akkvxGqVdIWOzY0"
}
