// Identidade individual; somente provisionamento administrativo confiável.
table clinica_admin {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int clinica_id {
      table = "clinica"
    }

    text nome filters=trim
    email email filters=trim|lower
    password senha {
      sensitive = true
      visibility = "internal"
    }
    bool ativo?=true
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
    {type: "btree", field: [{name: "clinica_id", op: "asc"}]}
  ]

  tags = ["vettech"]
}
