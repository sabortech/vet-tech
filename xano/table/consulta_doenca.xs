table consulta_doenca {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int consulta_id { table = "consulta" }
    int pet_id { table = "pet" }
    int veterinario_id { table = "veterinario" }
    int doenca_id { table = "doenca" }
    text origem_linha
    date data_diagnostico
    text estado
    text? observacoes?
    timestamp publicado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "consulta_id", op: "asc"}, {name: "origem_linha", op: "asc"}]}
    {type: "btree", field: [{name: "pet_id", op: "asc"}]}
  ]
  tags = ["vettech", "clinical"]
  guid = "9EF789yXjbs19noaCl_WBC-K9Rg"
}
