query "clinica/pets" verb=POST {
  api_group = "Authentication"
  auth = "clinica_admin"
  input {
    text nome filters=trim
    int especie_id
    int raca_id?
    text sexo? filters=trim
    date? data_nasc?
    int peso_atual?
    text cor_pelo? filters=trim
    int num_microchip?
    text foto?
  }
  stack {
    db.get clinica_admin {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "clinica_id"]
    } as $admin
    precondition ($admin != null && $admin.ativo == true && $admin.clinica_id != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }
    db.get clinica {
      field_name = "id"
      field_value = $admin.clinica_id
      output = ["id"]
    } as $clinica
    precondition ($clinica != null && $input.nome != "") {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }
    db.get especie {
      field_name = "id"
      field_value = $input.especie_id
      output = ["id"]
    } as $especie
    precondition ($especie != null) {
      error_type = "inputerror"
      error = "A espécie informada não existe."
    }
    conditional {
      if ($input.raca_id != null) {
        db.get raca {
          field_name = "id"
          field_value = $input.raca_id
          output = ["id", "especie_id"]
        } as $raca
        precondition ($raca != null && $raca.especie_id == $especie.id) {
          error_type = "inputerror"
          error = "A raça informada não pertence à espécie selecionada."
        }
      }
    }
    var $pet_criado { value = null }
    db.transaction {
      stack {
        db.add pet {
          data = {
            nome: $input.nome
            especie_id: $input.especie_id
            raca_id: $input.raca_id
            sexo: $input.sexo
            data_nasc: $input.data_nasc
            peso_atual: $input.peso_atual
            cor_pelo: $input.cor_pelo
            num_microchip: $input.num_microchip
            foto: $input.foto
            tutor_id: null
            clinica_id: $clinica.id
            disponivel_adocao: false
          }
        } as $pet
        db.add clinica_adocao_evento {
          data = {clinica_id: $clinica.id, admin_id: $admin.id, pet_id: $pet.id, acao: "cadastro"}
        } as $evento
        var.update $pet_criado { value = {id: $pet.id, nome: $pet.nome, disponivel_adocao: false} }
      }
    }
  }
  response = $pet_criado
  tags = ["vettech"]
}
