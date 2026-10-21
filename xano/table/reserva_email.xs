// Technical uniqueness reservation, never an authentication identity.
table reserva_email {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    email email filters=trim|lower { visibility = "internal" }
    text perfil { visibility = "internal" }
    int identidade_id? { visibility = "internal" }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]
  tags = ["vettech"]
  guid = "QxRF_UCB9XzsgxvsWrBOPfh5bpY"
}
