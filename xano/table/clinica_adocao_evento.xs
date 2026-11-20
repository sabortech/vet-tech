// Auditoria operacional interna; não contém dados clínicos ou credenciais.
table clinica_adocao_evento {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int clinica_id { table = "clinica" }
    int admin_id { table = "clinica_admin" }
    int pet_id { table = "pet" }
    text acao
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "pet_id", op: "asc"}]}
  ]
  tags = ["vettech"]
}
