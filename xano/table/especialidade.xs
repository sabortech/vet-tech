table especialidade {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text nome filters=trim
    text chave filters=trim|lower
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "chave", op: "asc"}]}
  ]

  tags = ["vettech"]
  guid = "rlzG3PaT6siKi5fenR28imtlSek"
}
