// Chat is separate from clinical records and grants no clinical authorization.
table support_ticket {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int tutor_id { table = "tutor" }
    int pet_id { table = "pet" }
    int? veterinario_id? { table = "veterinario" }
    text conversation_id
    text status
    json context
    text reason
    json messages
    json events
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "conversation_id", op: "asc"}]}
    {type: "btree", field: [{name: "tutor_id", op: "asc"}]}
    {type: "btree", field: [{name: "veterinario_id", op: "asc"}]}
  ]
  tags = ["vettech", "support-chat"]
  guid = "xWvb4CSV5AHns7lxVCq5IlRPf2E"
}
