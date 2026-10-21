table consulta {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int pet_id? {
      table = "pet"
    }
  
    int veterinario_id? {
      table = "veterinario"
    }
  
    date? data?
    text motivo? filters=trim
    text diagnostico? filters=trim
    text obs? filters=trim
    text? status?
    timestamp? agendada_para?
    text? fuso?
    timestamp? iniciada_em?
    timestamp? finalizada_em?
    date? data_atendimento?
    date? retorno_previsto?
    int versao?=0
    json? rascunho? {
      visibility = "internal"
    }
    text? operacao_chave? {
      visibility = "internal"
    }
    text? operacao_hash? {
      visibility = "internal"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "veterinario_id", op: "asc"}, {name: "agendada_para", op: "asc"}]}
    {type: "btree|unique", field: [{name: "pet_id", op: "asc"}, {name: "agendada_para", op: "asc"}]}
    {type: "btree|unique", field: [{name: "operacao_chave", op: "asc"}]}
  ]

  tags = ["vettech"]
  guid = "kslCqoKK1vCLeDJiNgzRQpoijpI"
}
