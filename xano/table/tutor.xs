table tutor {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text cpf filters=trim
    email email? filters=trim|lower
    text telefone? filters=trim
    text endereco? filters=trim
    password senha? {
      sensitive = true
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "wofHo9Q0mxDLcKRHvGob3A0iCyE"
}