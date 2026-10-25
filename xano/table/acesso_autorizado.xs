table acesso_autorizado {
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

    date? data_autorizacao?
    text status filters=trim
    timestamp? concedido_em?
    timestamp? revogado_em?
    int consulta_origem_id? {
      table = "consulta"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree|unique"
      field: [
        {name: "pet_id", op: "asc"}
        {name: "veterinario_id", op: "asc"}
      ]
    }
  ]

  tags = ["vettech"]
  guid = "AljyfL-XcUcvJutx2bKZmzZzIBA"
}
