table cadastro_google {
  auth=false
  schema {
    int id
    timestamp created_at?=now
    text prova_hash {visibility="internal"}
    text google_sub {visibility="internal"}
    email email {visibility="internal"}
    text nome {visibility="internal"}
    timestamp expira_em {visibility="internal"}
  }
  index=[
    {type:"primary",field:[{name:"id"}]}
    {type:"btree|unique",field:[{name:"prova_hash",op:"asc"}]}
  ]
}
