query "audit/{log_id}" verb=PATCH {
  api_group = "Prontuario"
  auth = "veterinario"
  input {
    int log_id
  }
  stack {
    throw {
      name = "accessdenied"
      value = "Registros de auditoria são imutáveis."
    }
  }
  response = null
}
