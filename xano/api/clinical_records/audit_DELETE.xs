query "audit/{log_id}" verb=DELETE {
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
  guid = "VpZ40tnUO_h24-RWHl6DvT3Ps74"
}
