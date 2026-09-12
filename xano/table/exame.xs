table exame {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pet_id? {
      table = "pet"
    }
  
    int consulta_id? {
      table = "consulta"
    }
  
    text tipo? filters=trim
    date? data?
    text resultado? filters=trim
    attachment arquivo?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "xKgFwRLbHJ5fdhdJY2s-D0S_4qM"
}