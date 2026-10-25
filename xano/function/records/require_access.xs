// actor_id comes exclusively from the veterinarian-authenticated endpoint.
function "records/require_access" {
  input {
    int veterinario_id
    int pet_id
    text acao
  }

  stack {
    precondition ($input.acao == "visualizacao" || $input.acao == "edicao" || $input.acao == "exportacao") {
      error_type = "accessdenied"
      error = "Operação não permitida."
    }

    db.get veterinario {
      field_name = "id"
      field_value = $input.veterinario_id
      output = ["id"]
    } as $veterinario

    precondition ($veterinario != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.get pet {
      field_name = "id"
      field_value = $input.pet_id
      output = ["id", "tutor_id"]
    } as $pet

    precondition ($pet != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query acesso_autorizado {
      where = $db.acesso_autorizado.pet_id == $input.pet_id && $db.acesso_autorizado.veterinario_id == $input.veterinario_id && $db.acesso_autorizado.status == "ativo"
      return = {type: "exists"}
    } as $permitido

    precondition ($permitido) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  }

  response = $pet
  guid = "h-RFtHwrMI2FuQrHVbMIaRBTcUQ"
}
