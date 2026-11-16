// Metadados internos de boas-vindas; sem endpoints CRUD públicos.
table welcome_email_attempt {
  auth = false
  schema {
    int id
    int event_id
    text state
    text provider_id?
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "event_id", op: "asc"}]}
  ]
  tags = ["vettech", "welcome-email"]
}
