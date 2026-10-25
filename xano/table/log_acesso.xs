table log_acesso {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int pet_id {
      table = "pet"
    }

    int veterinario_id {
      table = "veterinario"
    }

    timestamp data_hora?=now
    text acao filters=trim
    timestamp? ocorrido_em?
    int consulta_id? {
      table = "consulta"
    }

    int tutor_id? {
      table = "tutor"
    }

    text? operacao?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree"
      field: [
        {name: "pet_id", op: "asc"}
        {name: "ocorrido_em", op: "desc"}
      ]
    }
    {
      type : "btree|unique"
      field: [{name: "operacao", op: "asc"}]
    }
  ]

  tags = ["vettech"]
  guid = "bBxqV0b4-O4THzKGnUyX0MMuROY"
}
