function "Clinical/history" {
  input {
    int pet_id
  }
  stack {
    db.query consulta {
      where = $db.consulta.pet_id == $input.pet_id
      output = ["id", "pet_id", "veterinario_id", "status", "agendada_para", "iniciada_em", "finalizada_em", "motivo", "data_atendimento", "data", "diagnostico", "obs", "retorno_previsto", "versao"]
      sort = {
        consulta.data_atendimento: "desc"
      }
      return = {
        type: "list"
      }
    } as $consultations
    db.query vacina {
      where = $db.vacina.pet_id == $input.pet_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "vacina", "lote", "data_aplicacao", "data_prox_dose"]
      return = {
        type: "list"
      }
    } as $vacina
    db.query medicamento {
      where = $db.medicamento.pet_id == $input.pet_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "nome", "dosagem", "dose", "unidade", "frequencia", "via", "tipo", "data_inicio", "data_fim"]
      return = {
        type: "list"
      }
    } as $medicamento
    db.query exame {
      where = $db.exame.pet_id == $input.pet_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "tipo", "status", "data_solicitacao", "data_realizacao", "data", "resultado"]
      return = {
        type: "list"
      }
    } as $exame
    db.query consulta_doenca {
      where = $db.consulta_doenca.pet_id == $input.pet_id
      output = ["id", "pet_id", "consulta_id", "veterinario_id", "doenca_id", "data_diagnostico", "estado", "observacoes", "publicado_em"]
      return = {
        type: "list"
      }
    } as $consulta_doenca
    db.query pet_doenca {
      where = $db.pet_doenca.pet_id == $input.pet_id
      output = ["id", "pet_id", "doenca_id", "estado", "data_evolucao", "consulta_doenca_id"]
      return = {
        type: "list"
      }
    } as $pet_doenca
    db.query doenca {
      where = $db.doenca.id > 0
      output = ["id", "nome", "descricao", "tipo", "gravidade", "pet_id"]
      return = {
        type: "list"
      }
    } as $doenca
    api.lambda {
      code = "const consultations=$var.consultations.filter(x=>x.status==='finalizada'||!x.status);\nconst ids=new Set(consultations.map(x=>x.id));\nconst visible=rows=>rows.filter(x=>!x.consulta_id||ids.has(x.consulta_id));\nconst vaccines=visible($var.vacina), medications=visible($var.medicamento), exams=visible($var.exame), evolutions=visible($var.consulta_doenca);\nconst diseases=new Map($var.doenca.map(x=>[x.id,x]));\nconst evolutionById=new Map(evolutions.map(x=>[x.id,x]));\nconst conditions=$var.pet_doenca.filter(x=>evolutionById.has(x.consulta_doenca_id)).map(x=>({...x,nome:diseases.get(x.doenca_id)?.nome||'Doença',consulta_id:evolutionById.get(x.consulta_doenca_id).consulta_id,veterinario_id:evolutionById.get(x.consulta_doenca_id).veterinario_id}));\nconst legacy=$var.doenca.filter(x=>x.pet_id===$input.pet_id).map(x=>({...x,legado:true}));\nreturn {consultas:consultations,vacinas:vaccines,medicamentos:medications,exames:exams,diagnosticos:evolutions.map(x=>({...x,nome:diseases.get(x.doenca_id)?.nome||'Doença'})),doencas:[...conditions,...legacy]};"
      timeout = 5
    } as $history
  }
  response = $history
  tags = ["vettech", "clinical"]
  guid = "gdGDX6Mo3RIlrkoRy56tDgJqSeY"
}
