table clinica {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text cnpj? filters=trim
    text endereco? filters=trim
    text telefone? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "7hx-1KHbBummP2M0eefPvEEuviQ"
}