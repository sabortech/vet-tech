table raca {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    text nome? filters=trim
    text? nome_normalizado? {
      visibility = "internal"
    }

    int especie_id {
      table = "especie"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree|unique"
      field: [
        {name: "especie_id", op: "asc"}
        {name: "nome_normalizado", op: "asc"}
      ]
    }
  ]

  tags = ["vettech"]
  guid = "-pZGOE_jMwlKyzTfZCyeu-NFbdM"
}
