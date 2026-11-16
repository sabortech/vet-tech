// Internal security metadata; never create public CRUD endpoints.
table password_lock {
  auth = false
  schema {
    int id
    text key
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree|unique", field: [{name: "key", op: "asc"}]}
  ]
  tags = ["vettech", "password-security"]
}
