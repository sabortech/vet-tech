table acesso_autorizado {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pet_id? {
      table = "pet"
    }
  
    int veterinario_id? {
      table = "veterinario"
    }
  
    date? data_autorizacao?
    text status? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "AljyfL-XcUcvJutx2bKZmzZzIBA"
}