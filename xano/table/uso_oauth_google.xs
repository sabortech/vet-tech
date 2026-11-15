// Single-use marker: inserting an existing key fails on the unique index, so an
// OAuth state can be consumed only once, even under concurrent requests.
// Rows are kept; never expose this table.
table uso_oauth_google {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text chave {
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "chave", op: "asc"}]}
  ]

  tags = ["vettech", "google-login"]
  guid = "iK0yifbPyXtdkbyKvNa82j9MMow"
}
