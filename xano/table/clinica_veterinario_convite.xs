table clinica_veterinario_convite {
  auth = false
  schema {
    int id
    int clinica_id { table = "clinica" }
    int veterinario_id { table = "veterinario" }
    int admin_id { table = "clinica_admin" }
    text status
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree", field: [{name: "veterinario_id", op: "asc"}]}
  ]
  tags = ["vettech"]
}
