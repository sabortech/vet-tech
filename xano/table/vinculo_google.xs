// Google account (sub) linked to exactly one Vet Tech identity and vice versa.
// Technical table, never an authentication identity; no Google tokens stored.
table vinculo_google {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text google_sub {
      visibility = "internal"
    }

    text perfil {
      visibility = "internal"
    }

    int identidade_id {
      visibility = "internal"
    }

    email email_no_vinculo filters=trim|lower {
      visibility = "internal"
    }

    timestamp? ultimo_uso_em? {
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "google_sub", op: "asc"}]}
    {
      type : "btree|unique"
      field: [{name: "perfil", op: "asc"}, {name: "identidade_id", op: "asc"}]
    }
  ]

  tags = ["vettech", "google-login"]
  guid = "3wLS1t1vR8iAWRdCMN1qEUf-ec8"
}
