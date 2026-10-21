function "Clinical/audit" {
  input {
    int pet_id
    int veterinario_id?
    int tutor_id?
    int consulta_id?
    text acao
    text? operacao?
  }
  stack {
    db.add log_acesso {
      data = {
        pet_id: $input.pet_id, veterinario_id: $input.veterinario_id,
        tutor_id: $input.tutor_id, consulta_id: $input.consulta_id,
        acao: $input.acao, ocorrido_em: "now", operacao: $input.operacao
      }
    } as $audit_row
  }
  response = $audit_row.id
  tags = ["vettech", "clinical"]
  guid = "Lwulc23UM1EQ1ZLUuComqIwP_XQ"
}
