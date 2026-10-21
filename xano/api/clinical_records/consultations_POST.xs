query "consultations" verb=POST {
  api_group = "Prontuario"
  auth = "veterinario"
  input {
    int pet_id
    date data
    text motivo filters=trim
    text diagnostico? filters=trim
    text obs? filters=trim
  }
  stack {
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $clinical_guard
    function.run "records/require_access" {
      input = {veterinario_id: $auth.id, pet_id: $input.pet_id, acao: "edicao"}
    } as $pet
        db.add consulta {
          data = {pet_id: $input.pet_id, veterinario_id: $auth.id, data: $input.data, data_atendimento: $input.data, status: "finalizada", motivo: $input.motivo, diagnostico: $input.diagnostico, obs: $input.obs}
        } as $consulta
        function.run "records/audit" {
          input = {pet_id: $input.pet_id, veterinario_id: $auth.id, acao: "edicao"}
        } as $log_id
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
      }
    }
  }
  response = $consulta
}
