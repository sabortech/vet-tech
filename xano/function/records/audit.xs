// Call inside the same transaction as the protected operation. Never catch errors.
function "records/audit" {
  input {
    int pet_id
    int veterinario_id
    text acao
  }
  stack {
    precondition ($input.acao == "visualizacao" || $input.acao == "edicao" || $input.acao == "exportacao") {
      error_type = "inputerror"
      error = "Ação de auditoria inválida."
    }
    db.add log_acesso {
      data = {pet_id: $input.pet_id, veterinario_id: $input.veterinario_id, acao: $input.acao, data_hora: "now", ocorrido_em: "now"}
    } as $log
  }
  response = $log.id
}
