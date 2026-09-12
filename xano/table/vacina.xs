table vacina {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pet_id? {
      table = "pet"
    }
  
    text vacina? filters=trim
    date? data_aplicacao?
    text lote? filters=trim
    date? data_prox_dose?
    int veterinario_id? {
      table = "veterinario"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "H8ZntYbO9MYOiuEzhjFvSa0Viws"
}