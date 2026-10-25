query "records/tutor" verb=GET {
  api_group = "Prontuario"
  auth = "tutor"
  input {
    int pet_id
  }
  stack {
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $clinical_guard
    function.run "records/require_owner" {
      input = {tutor_id: $auth.id, pet_id: $input.pet_id}
    } as $pet
        db.query consulta {
          where = $db.consulta.pet_id == $input.pet_id && ($db.consulta.status == "finalizada" || $db.consulta.status == null || $db.consulta.status == "")
          output = ["id", "pet_id", "veterinario_id", "data", "data_atendimento", "motivo", "diagnostico", "obs", "retorno_previsto", "status"]
          return = {type: "list"}
        } as $consultas
        db.query exame {
          where = $db.exame.pet_id == $input.pet_id
          return = {type: "list"}
        } as $exames
        api.lambda {
          code = """
            const ids = new Set($var.consultas.map(row => row.id));
            return $var.exames.filter(row => !row.consulta_id || ids.has(row.consulta_id));
            """
          timeout = 5
        } as $exames_visiveis
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
      }
    }
  }
  response = {pet_id: $pet.id, consultas: $consultas, exames: $exames_visiveis}
  guid = "q8IL2Nz9lqErra_UqlTxUrU3fjc"
}
