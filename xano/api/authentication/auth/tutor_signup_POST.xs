query "tutor/signup" verb=POST {
  api_group = "Authentication"

  input {
    text nome filters=trim
    text cpf filters=trim
    email email filters=trim|lower
    text telefone filters=trim
    text endereco filters=trim
    password password
  }

  stack {
    precondition (
      $input.nome != "" &&
      $input.cpf != "" &&
      $input.email != "" &&
      $input.telefone != "" &&
      $input.endereco != "" &&
      $input.password != ""
    ) {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }

    precondition ($input.cpf|regex_test:"^[0-9. -]+$") {
      error_type = "inputerror"
      error = "Informe um CPF válido."
    }

    var $cpf_digits {
      value = $input.cpf|regex_replace:"[^0-9]":""
    }

    precondition ($cpf_digits|regex_test:"^[0-9]{11}$") {
      error_type = "inputerror"
      error = "Informe um CPF válido."
    }

    precondition (
      $cpf_digits != "00000000000" &&
      $cpf_digits != "11111111111" &&
      $cpf_digits != "22222222222" &&
      $cpf_digits != "33333333333" &&
      $cpf_digits != "44444444444" &&
      $cpf_digits != "55555555555" &&
      $cpf_digits != "66666666666" &&
      $cpf_digits != "77777777777" &&
      $cpf_digits != "88888888888" &&
      $cpf_digits != "99999999999"
    ) {
      error_type = "inputerror"
      error = "Informe um CPF válido."
    }

    var $cpf_with_prefix {
      value = "1"|concat:$cpf_digits
    }

    var $cpf_number {
      value = $cpf_with_prefix|to_int
    }

    var $cpf_d0 {
      value = $cpf_number|divide:10000000000|floor|modulus:10
    }

    var $cpf_d1 {
      value = $cpf_number|divide:1000000000|floor|modulus:10
    }

    var $cpf_d2 {
      value = $cpf_number|divide:100000000|floor|modulus:10
    }

    var $cpf_d3 {
      value = $cpf_number|divide:10000000|floor|modulus:10
    }

    var $cpf_d4 {
      value = $cpf_number|divide:1000000|floor|modulus:10
    }

    var $cpf_d5 {
      value = $cpf_number|divide:100000|floor|modulus:10
    }

    var $cpf_d6 {
      value = $cpf_number|divide:10000|floor|modulus:10
    }

    var $cpf_d7 {
      value = $cpf_number|divide:1000|floor|modulus:10
    }

    var $cpf_d8 {
      value = $cpf_number|divide:100|floor|modulus:10
    }

    var $cpf_d9 {
      value = $cpf_number|divide:10|floor|modulus:10
    }

    var $cpf_d10 {
      value = $cpf_number|modulus:10
    }

    var $cpf_sum1 {
      value = 0
    }

    math.add $cpf_sum1 {
      value = $cpf_d0|multiply:10
    }

    math.add $cpf_sum1 {
      value = $cpf_d1|multiply:9
    }

    math.add $cpf_sum1 {
      value = $cpf_d2|multiply:8
    }

    math.add $cpf_sum1 {
      value = $cpf_d3|multiply:7
    }

    math.add $cpf_sum1 {
      value = $cpf_d4|multiply:6
    }

    math.add $cpf_sum1 {
      value = $cpf_d5|multiply:5
    }

    math.add $cpf_sum1 {
      value = $cpf_d6|multiply:4
    }

    math.add $cpf_sum1 {
      value = $cpf_d7|multiply:3
    }

    math.add $cpf_sum1 {
      value = $cpf_d8|multiply:2
    }

    math.mod $cpf_sum1 {
      value = 11
    }

    var $cpf_check1 {
      value = 0
    }

    conditional {
      if ($cpf_sum1 > 1) {
        var.update $cpf_check1 {
          value = 11
        }

        math.sub $cpf_check1 {
          value = $cpf_sum1
        }
      }
    }

    precondition ($cpf_d9 == $cpf_check1) {
      error_type = "inputerror"
      error = "Informe um CPF válido."
    }

    var $cpf_sum2 {
      value = 0
    }

    math.add $cpf_sum2 {
      value = $cpf_d0|multiply:11
    }

    math.add $cpf_sum2 {
      value = $cpf_d1|multiply:10
    }

    math.add $cpf_sum2 {
      value = $cpf_d2|multiply:9
    }

    math.add $cpf_sum2 {
      value = $cpf_d3|multiply:8
    }

    math.add $cpf_sum2 {
      value = $cpf_d4|multiply:7
    }

    math.add $cpf_sum2 {
      value = $cpf_d5|multiply:6
    }

    math.add $cpf_sum2 {
      value = $cpf_d6|multiply:5
    }

    math.add $cpf_sum2 {
      value = $cpf_d7|multiply:4
    }

    math.add $cpf_sum2 {
      value = $cpf_d8|multiply:3
    }

    math.add $cpf_sum2 {
      value = $cpf_d9|multiply:2
    }

    math.mod $cpf_sum2 {
      value = 11
    }

    var $cpf_check2 {
      value = 0
    }

    conditional {
      if ($cpf_sum2 > 1) {
        var.update $cpf_check2 {
          value = 11
        }

        math.sub $cpf_check2 {
          value = $cpf_sum2
        }
      }
    }

    precondition ($cpf_d10 == $cpf_check2) {
      error_type = "inputerror"
      error = "Informe um CPF válido."
    }

    db.get tutor {
      field_name = "cpf"
      field_value = $cpf_digits
      output = ["id"]
    } as $existing_cpf

    precondition ($existing_cpf == null) {
      error_type = "inputerror"
      error = "Já existe uma conta com esse CPF ou e-mail."
    }

    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $existing_email

    precondition ($existing_email == null) {
      error_type = "inputerror"
      error = "Já existe uma conta com esse CPF ou e-mail."
    }

    db.add tutor {
      data = {
        nome     : $input.nome
        cpf      : $cpf_digits
        email    : $input.email
        telefone : $input.telefone
        endereco : $input.endereco
        password : $input.password
      }
    } as $tutor
  }

  response = {success: true}
  guid = "Sf0P9fazACZFbxFTNcfSQqqKHqY"
}
