// Internal security metadata; never create public CRUD endpoints.
table password_origin {
  auth = false
  schema {
    int id
    text key
    json times
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree|unique", field: [{name: "key", op: "asc"}]},
    {type: "btree", field: [{name: "updated_at", op: "asc"}]}
  ]
  tags = ["vettech", "password-security"]
}
