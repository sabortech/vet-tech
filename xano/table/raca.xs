table raca {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    int especie_id? {
      table = "especie"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "-pZGOE_jMwlKyzTfZCyeu-NFbdM"
}