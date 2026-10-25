// Insert/delete inside the SAME transaction serializes operations for one pet.
// Never expose this technical table through a public endpoint.
table clinical_lock {
  auth = false

  schema {
    int id
    int pet_id {
      table = "pet"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "pet_id", op: "asc"}]}
  ]

  tags = ["vettech", "clinical"]
  guid = "bZUOoufCD94fh7TiLrybYS-Ivx0"
}
