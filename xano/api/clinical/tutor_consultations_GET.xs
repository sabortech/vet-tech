query "tutor/consultas" verb=GET {
  api_group = "Clinical"
  auth = "tutor"
  input {
    int pet_id
  }
  stack {
    function.run "Clinical/assert_owner" {
      input = {
        pet_id: $input.pet_id, tutor_id: $auth.id
      }
    } as $owned
    db.query consulta {
      where = $db.consulta.pet_id == $owned.id
      output = ["id", "pet_id", "veterinario_id", "status", "agendada_para", "iniciada_em", "finalizada_em", "motivo", "data_atendimento", "data", "diagnostico", "obs", "retorno_previsto", "versao"]
      sort = {
        consulta.agendada_para: "asc"
      }
      return = {
        type: "list"
      }
    } as $rows
    api.lambda {
      code = "return $var.rows.map(r=>r.status===\"finalizada\"||!r.status?r:{id:r.id,pet_id:r.pet_id,veterinario_id:r.veterinario_id,status:r.status,agendada_para:r.agendada_para,motivo:r.motivo});"
      timeout = 5
    } as $reply
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "OaYtKqhpmP5Sg0UFHePiWqFoyZg"
}
