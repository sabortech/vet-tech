table veterinario {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text cmv? filters=trim
    text especialidade? filters=trim
    email email? filters=trim|lower
    text telefone? filters=trim
    int clinica_id? {
      table = "clinica"
    }
  
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
  guid = "AeeZiyYEYEP_CqAeTCUGLB5pnEc"
}