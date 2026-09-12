table medicamento {
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
    int dosagem?
    date? data_inicio?
    date? data_fim?
    text tipo? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "OYRhCjBjAuBafFm186R_aXltOdo"
}