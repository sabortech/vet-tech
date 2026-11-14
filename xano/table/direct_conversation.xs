// Private non-clinical pair: no pet, attendance status or assistant context.
table direct_conversation {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    text pair_key
    int tutor_id { table = "tutor" }
    int veterinario_id { table = "veterinario" }
    json messages
    json events
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "pair_key", op: "asc"}]}
    {type: "btree", field: [{name: "tutor_id", op: "asc"}]}
    {type: "btree", field: [{name: "veterinario_id", op: "asc"}]}
  ]
  tags = ["vettech", "direct-messaging"]
  guid = "T8tFKvyJbvF3N_G2JEcGsRCg7xQ"
}
