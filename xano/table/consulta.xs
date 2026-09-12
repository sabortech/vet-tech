table consulta {
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
  
    date? data?
    text motivo? filters=trim
    text diagnostico? filters=trim
    text obs? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "kslCqoKK1vCLeDJiNgzRQpoijpI"
}