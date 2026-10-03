table doenca {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pet_id? {
      table = "pet"
    }
  
    text nome? filters=trim
    text descricao? filters=trim
    text tipo? filters=trim
    text gravidade? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "vCX4b9VoBQzdRYNHa_-WN-O7qCo"
}