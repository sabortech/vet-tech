function "Clinical/assert_consultation" {
  input {
    int consulta_id
    int veterinario_id
  }
  stack {
    db.query consulta {
      where = $db.consulta.id == $input.consulta_id && $db.consulta.veterinario_id == $input.veterinario_id
      return = {
        type: "single"
      }
      output = ["id", "pet_id", "veterinario_id", "status", "versao", "agendada_para", "iniciada_em", "finalizada_em", "motivo", "rascunho", "data_atendimento"]
    } as $consultation
    precondition ($consultation != null) {
      error_type = "notfound"
      error = "Consulta não disponível."
    }
  }
  response = $consultation
  tags = ["vettech", "clinical"]
  guid = "XEJeFXXkeB8l2SRLO9eVX3XE1vg"
}
