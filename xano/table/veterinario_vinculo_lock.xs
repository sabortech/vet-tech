table veterinario_vinculo_lock {
  auth = false
  schema {
    int id
    int veterinario_id { table = "veterinario" }
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree|unique", field: [{name: "veterinario_id", op: "asc"}]}
  ]
  tags = ["vettech"]
}
