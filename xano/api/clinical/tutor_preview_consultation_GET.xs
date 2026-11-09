query "tutor/pets/{pet_id}/consultas/{consulta_id}/previa-pdf" verb=GET {
  api_group = "Clinical"
  auth = "tutor"
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
        function.run "Clinical/assert_owner" {
          input = {pet_id: $input.pet_id, tutor_id: $auth.id}
        } as $authorized
        function.run "Clinical/consultation_document" {
          input = {pet_id: $authorized.id, consulta_id: $input.consulta_id, pet_nome: $authorized.nome}
        } as $document
        function.run "Clinical/audit" {
          input = {pet_id: $authorized.id, consulta_id: $input.consulta_id, tutor_id: $auth.id, veterinario_id: $document.consulta.veterinario_id, acao: "visualizar_previa_pdf", operacao: null}
        } as $audit_id
        api.lambda {
          code = "return {...$var.document,auditoria_id:$var.audit_id};"
          timeout = 5
        } as $authorized_document
        var.update $reply { value = $authorized_document }
      }
    }
  }
  response = $reply
  tags = ["vettech", "clinical"]
}
