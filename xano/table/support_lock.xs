// Insert/delete only within the same transaction; no public CRUD.
table support_lock {
  auth = false
  schema {
    int id
    text key
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "key", op: "asc"}]}
  ]
  tags = ["vettech", "support-chat"]
  guid = "-TOPUVhh9vAoM9IhVjpQhAugJV8"
}
