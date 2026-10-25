query "exams" verb=POST {
  api_group = "Prontuario"
  auth = "veterinario"
  input {
    int pet_id
    int? consulta_id?
    text tipo filters=trim
    date data
    text resultado? filters=trim
    attachment arquivo?
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
        function.run "records/validate_exam" {
          input = {pet_id: $input.pet_id, consulta_id: $input.consulta_id}
        } as $validated_pet
        db.add exame {
          data = {pet_id: $input.pet_id, consulta_id: $input.consulta_id, tipo: $input.tipo, data: $input.data, resultado: $input.resultado, arquivo: $input.arquivo}
        } as $exame
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
  response = $exame
  guid = "Gkc66lzZoSLAK3uktYspPbtFWqE"
}
