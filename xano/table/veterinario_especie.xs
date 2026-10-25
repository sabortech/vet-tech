table veterinario_especie {
  auth = false

  schema {
    int id
    int veterinario_id {
      table = "veterinario"
    }

    int especie_id {
      table = "especie"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [
        {name: "veterinario_id", op: "asc"}
        {name: "especie_id", op: "asc"}
      ]
    }
  ]

  tags = ["vettech"]
  guid = "E2oNLEmgqI3hiIsLHL_JIU942Xc"
}
