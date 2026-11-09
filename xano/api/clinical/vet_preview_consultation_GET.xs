query "veterinario/pets/{pet_id}/consultas/{consulta_id}/previa-pdf" verb=GET {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    int pet_id
    int consulta_id
  }
  stack {
    precondition ($input.pet_id > 0 && $input.consulta_id > 0) {
      error_type = "inputerror"
      error = "Consulta inválida."
    }
    var $reply { value = null }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {pet_id: $input.pet_id}
        } as $clinical_guard
        function.run "Clinical/assert_access" {
          input = {pet_id: $input.pet_id, veterinario_id: $auth.id}
        } as $authorized
        function.run "Clinical/consultation_document" {
          input = {pet_id: $authorized.id, consulta_id: $input.consulta_id, pet_nome: $authorized.nome}
        } as $document
        function.run "Clinical/audit" {
          input = {pet_id: $authorized.id, consulta_id: $input.consulta_id, veterinario_id: $auth.id, acao: "visualizar_previa_pdf", operacao: null}
        } as $audit_id
        api.lambda {
          code = "return {...$var.document,auditoria_id:$var.audit_id};"
          timeout = 5
        } as $authorized_document
        var.update $reply { value = $authorized_document }
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "clinical"]
}
