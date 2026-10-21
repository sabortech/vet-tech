table veterinario {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    text nome? filters=trim
    text cmv? filters=trim
    text crmv? filters=trim|upper
    text crmv_uf? filters=trim|upper
    text especialidade? filters=trim
    email email? filters=trim|lower
    text telefone? filters=trim
    int clinica_id? {
      table = "clinica"
    }

    password senha? {
      sensitive = true
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
    {
      type : "btree|unique"
      field: [{name: "crmv_uf", op: "asc"}, {name: "crmv", op: "asc"}]
    }
  ]

  tags = ["vettech"]
  guid = "AeeZiyYEYEP_CqAeTCUGLB5pnEc"
}
