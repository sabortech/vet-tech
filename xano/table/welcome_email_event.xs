// Metadados internos de boas-vindas; sem endpoints CRUD públicos.
table welcome_email_event {
  auth = false
  schema {
    int id
    text key
    text profile
    int identity_id
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "key", op: "asc"}]}
  ]
  tags = ["vettech", "welcome-email"]
}
