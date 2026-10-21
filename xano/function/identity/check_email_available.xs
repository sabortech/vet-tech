function "Identity/check_email_available" {
  input {
    email email filters=trim|lower
  }
  stack {
    db.get tutor {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $tutor
    db.get veterinario {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $veterinario
    db.get reserva_email {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $reservation
    precondition ($tutor == null && $veterinario == null && $reservation == null) {
      error_type = "inputerror"
      error = "Não foi possível cadastrar: e-mail já utilizado."
    }
  }
  response = null
  tags = ["vettech"]
  guid = "BrcdNYyQyDs08GRC5skiPWbxyZI"
}
