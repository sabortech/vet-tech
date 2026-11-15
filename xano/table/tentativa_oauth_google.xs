// Pending Google OAuth attempt. Stores only the hash of the state; the row is
// deleted when consumed. Never expose this technical table through an endpoint.
table tentativa_oauth_google {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text state_hash {
      visibility = "internal"
    }

    text code_verifier {
      visibility = "internal"
    }

    timestamp expira_em {
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "state_hash", op: "asc"}]}
  ]

  tags = ["vettech", "google-login"]
  guid = "kh55nNub1Wz5eScLpdg6dszzHDk"
}
