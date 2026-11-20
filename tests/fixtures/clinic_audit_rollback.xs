// Diagnóstico isolado: falha na inserção de auditoria deve reverter o pet.
function "Testing/clinic_audit_rollback" {
  input {
    int clinica_id
    int admin_id
    int especie_id
    int existing_event_id
    text nome
  }
  stack {
    db.transaction {
      stack {
        db.add pet {
          data = {nome: $input.nome, especie_id: $input.especie_id, tutor_id: null, clinica_id: $input.clinica_id, disponivel_adocao: false}
        } as $pet
        db.add clinica_adocao_evento {
          data = {id: $input.existing_event_id, clinica_id: $input.clinica_id, admin_id: $input.admin_id, pet_id: $pet.id, acao: "cadastro"}
        } as $evento
      }
    }
  }
  response = {id: $pet.id}
  history = false
}
