query pets verb=POST {
  api_group = "Pet"
  auth = "tutor"

  input {
    text nome filters=trim
    int especie_id
    int raca_id?
    text sexo? filters=trim
    date? data_nasc?
    int peso_atual?
    text cor_pelo? filters=trim
    int num_microchip?
    file? foto?
  }

  stack {
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
      
        precondition ($raca != null) {
          error_type = "inputerror"
          error = "A raça informada não existe."
        }
      
        precondition ($raca.especie_id == $input.especie_id) {
          error_type = "inputerror"
          error = "A raça informada não pertence à espécie selecionada."
        }
      }
    }
  
    var $foto_pet {
      value = null
    }
  
    conditional {
      if ($input.foto != null) {
        storage.create_image {
          value = $input.foto
          access = "private"
          filename = $input.foto.name
        } as $foto_enviada
      
        var.update $foto_pet {
          value = $foto_enviada
        }
      }
    }
  
    db.add pet {
      data = {
        nome         : $input.nome
        especie_id   : $input.especie_id
        raca_id      : $input.raca_id
        sexo         : $input.sexo
        data_nasc    : $input.data_nasc
        peso_atual   : $input.peso_atual
        cor_pelo     : $input.cor_pelo
        num_microchip: $input.num_microchip
        foto         : $foto_pet
        tutor_id     : $auth.id
      }
    } as $pet
  }

  response = {
    id           : $pet.id
    nome         : $pet.nome
    especie_id   : $pet.especie_id
    raca_id      : $pet.raca_id
    sexo         : $pet.sexo
    data_nasc    : $pet.data_nasc
    peso_atual   : $pet.peso_atual
    cor_pelo     : $pet.cor_pelo
    num_microchip: $pet.num_microchip
    tutor_id     : $pet.tutor_id
  }

  guid = "QR7_QlgmV6JnQRwMbU4jvbkANkc"
}