table pet_doenca {
  auth = false
  schema {
    int id
    int pet_id { table = "pet" }
    int doenca_id { table = "doenca" }
    text estado
    date data_evolucao
    timestamp atualizado_em?=now
    int consulta_doenca_id { table = "consulta_doenca" }
    int versao?=0
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "pet_id", op: "asc"}, {name: "doenca_id", op: "asc"}]}
  ]
  tags = ["vettech", "clinical"]
  guid = "ShQnC63wVXtd92-Cz3Vf9Ky5bRo"
}
