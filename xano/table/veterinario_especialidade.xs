table veterinario_especialidade {
  auth = false

  schema {
    int id
    int veterinario_id {
      table = "veterinario"
    }

    int especialidade_id {
      table = "especialidade"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [
        {name: "veterinario_id", op: "asc"}
        {name: "especialidade_id", op: "asc"}
      ]
    }
  ]

  tags = ["vettech"]
  guid = "gT2wgQ0Q8pkdHwGULwm9YY233ng"
}
