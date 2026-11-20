// Provisionamento interno: não expor como endpoint público.
function "Identity/create_clinica_admin" {
  input {
    int clinica_id
    text nome filters=trim
    email email filters=trim|lower
    password senha
  }
  stack {
    db.get clinica {
      field_name = "id"
      field_value = $input.clinica_id
      output = ["id"]
    } as $clinica
    precondition ($clinica != null && $input.nome != "" && $input.email != "" && $input.senha != "") {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }
    function.run "Identity/check_email_available" {
      input = {email: $input.email}
    } as $email_check
    db.transaction {
      stack {
        db.add reserva_email {
          data = {email: $input.email, perfil: "clinica"}
        } as $reservation
        db.add clinica_admin {
          data = {clinica_id: $clinica.id, nome: $input.nome, email: $input.email, senha: $input.senha, ativo: true}
        } as $admin
        db.edit reserva_email {
          field_name = "id"
          field_value = $reservation.id
          data = {identidade_id: $admin.id}
        } as $completed
      }
    }
  }
  response = {identidade_id: $admin.id}
  history = false
  tags = ["vettech"]
}
