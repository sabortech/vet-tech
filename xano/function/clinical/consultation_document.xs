// Caller must authorize the pet inside its transaction before invoking this function.
function "Clinical/consultation_document" {
  input {
    int pet_id
    int consulta_id
    text pet_nome
  }
  stack {
    db.query consulta {
      join = {
        veterinario: {
          table: "veterinario"
          type: "left"
          where: $db.consulta.veterinario_id == $db.veterinario.id
        }
      }
      eval = {veterinario_nome: $db.veterinario.nome}
      where = $db.consulta.id == $input.consulta_id && $db.consulta.pet_id == $input.pet_id
      output = ["id", "pet_id", "veterinario_id", "veterinario_nome", "status", "agendada_para", "iniciada_em", "finalizada_em", "motivo", "data_atendimento", "data", "diagnostico", "obs", "retorno_previsto"]
      return = {type: "single"}
    } as $consult
    precondition ($consult != null) {
      error_type = "notfound"
      error = "Consulta não disponível."
    }
    precondition ($consult.status == "finalizada") {
      error_type = "inputerror"
      error = "Somente consultas finalizadas podem ser exportadas."
    }
    db.query vacina {
      join = {
        veterinario: {
          table: "veterinario"
          type: "left"
          where: $db.vacina.veterinario_id == $db.veterinario.id
        }
      }
      eval = {veterinario_nome: $db.veterinario.nome}
      where = $db.vacina.pet_id == $input.pet_id && $db.vacina.consulta_id == $input.consulta_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "veterinario_nome", "vacina", "lote", "data_aplicacao", "data_prox_dose"]
      return = {
        type: "list"
      }
    } as $vacina
    db.query medicamento {
      join = {
        veterinario: {
          table: "veterinario"
          type: "left"
          where: $db.medicamento.veterinario_id == $db.veterinario.id
        }
      }
      eval = {veterinario_nome: $db.veterinario.nome}
      where = $db.medicamento.pet_id == $input.pet_id && $db.medicamento.consulta_id == $input.consulta_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "veterinario_nome", "nome", "dosagem", "dose", "unidade", "frequencia", "via", "tipo", "data_inicio", "data_fim"]
      return = {
        type: "list"
      }
    } as $medicamento
    db.query exame {
      join = {
        veterinario: {
          table: "veterinario"
          type: "left"
          where: $db.exame.veterinario_id == $db.veterinario.id
        }
      }
      eval = {veterinario_nome: $db.veterinario.nome}
      where = $db.exame.pet_id == $input.pet_id && $db.exame.consulta_id == $input.consulta_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "veterinario_nome", "tipo", "status", "data_solicitacao", "data_realizacao", "data", "resultado"]
      return = {
        type: "list"
      }
    } as $exame
    db.query consulta_doenca {
      join = {
        doenca: {table: "doenca", where: $db.consulta_doenca.doenca_id == $db.doenca.id}
        veterinario: {
          table: "veterinario"
          type: "left"
          where: $db.consulta_doenca.veterinario_id == $db.veterinario.id
        }
      }
      eval = {veterinario_nome: $db.veterinario.nome, nome: $db.doenca.nome}
      where = $db.consulta_doenca.pet_id == $input.pet_id && $db.consulta_doenca.consulta_id == $input.consulta_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "veterinario_nome", "doenca_id", "data_diagnostico", "estado", "observacoes", "publicado_em", "nome"]
      return = {
        type: "list"
      }
    } as $consulta_doenca
    api.lambda {
      code = "return {consulta:$var.consult,pet:{id:$input.pet_id,nome:$input.pet_nome},vacinas:$var.vacina,medicamentos:$var.medicamento,exames:$var.exame,diagnosticos:$var.consulta_doenca.map(r=>({...r,nome:r.nome||'Não informado'}))};"
      timeout = 5
    } as $document
  }
  response = $document
  tags = ["vettech", "clinical"]
}
