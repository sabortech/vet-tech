// Internal security metadata; never create public CRUD endpoints.
table password_challenge {
  auth = false
  schema {
    int id
    text key
    text public_id?
    text grant_digest?
    text profile?
    int identity_id?
    json state
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]},
    {type: "btree|unique", field: [{name: "key", op: "asc"}]},
    {type: "btree", field: [{name: "public_id", op: "asc"}]},
    {type: "btree", field: [{name: "grant_digest", op: "asc"}]},
    {type: "btree", field: [{name: "updated_at", op: "asc"}]}
  ]
  tags = ["vettech", "password-security"]
}
