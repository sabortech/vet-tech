table tutor {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text cpf filters=trim
    email email filters=trim|lower
    text telefone? filters=trim
    text endereco? filters=trim
    password password {
      sensitive = true
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["vettech"]
  guid = "wofHo9Q0mxDLcKRHvGob3A0iCyE"
}