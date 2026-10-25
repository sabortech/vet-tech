query "audit/{log_id}" verb=PATCH {
  api_group = "Prontuario"
  auth = "veterinario"
  input {
    int log_id
  }
  stack {
    precondition (false) {
      error_type = "accessdenied"
      error = "Registros de auditoria são imutáveis."
    }
  }
  response = null
  guid = "h1hwh-7K2HKNNGnkPhOfTlmjhCc"
}
