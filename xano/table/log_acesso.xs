table log_acesso {
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
  
    date? data_hora?
    text acao? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "bBxqV0b4-O4THzKGnUyX0MMuROY"
}