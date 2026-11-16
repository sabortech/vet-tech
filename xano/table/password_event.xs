// Internal security metadata; never create public CRUD endpoints.
table password_event {
  auth = false
  schema {
    int id
    text profile?
    int identity_id?
    text purpose
    text outcome
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree", field: [{name: "created_at", op: "asc"}]}
  ]
  tags = ["vettech", "password-security"]
}
