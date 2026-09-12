table pet {
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
  
    int raca_id? {
      table = "raca"
    }
  
    text sexo? filters=trim
    date? data_nasc?
    int peso_atual?
    text cor_pelo? filters=trim
    int num_microchip?
    image? foto?
    int tutor_id? {
      table = "tutor"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["vettech"]
  guid = "cSr5TloxRuULn6FexKIho5f_jsE"
}