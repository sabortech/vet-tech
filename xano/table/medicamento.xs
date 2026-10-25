table medicamento {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pet_id? {
      table = "pet"
    }
  
    text nome? filters=trim
    int dosagem?
    decimal? dose?
    text? unidade?
    text? frequencia?
    text? via?
    int veterinario_id? { table = "veterinario" }
    int consulta_id? { table = "consulta" }
    text? origem_linha?
    date? data_inicio?
    date? data_fim?
    text tipo? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "consulta_id", op: "asc"}, {name: "origem_linha", op: "asc"}]}
  ]

  tags = ["vettech"]
  guid = "OYRhCjBjAuBafFm186R_aXltOdo"
}
