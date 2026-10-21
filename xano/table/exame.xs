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
    // Optional legacy upload; new structured examinations do not require a file.
    attachment? arquivo?
    text? status?
    date? data_solicitacao?
    date? data_realizacao?
    int veterinario_id? { table = "veterinario" }
    text? origem_linha?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "consulta_id", op: "asc"}, {name: "origem_linha", op: "asc"}]}
  ]

  tags = ["vettech"]
  guid = "xKgFwRLbHJ5fdhdJY2s-D0S_4qM"
}
