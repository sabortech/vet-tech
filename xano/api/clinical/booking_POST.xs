query "tutor/consultas" verb=POST {
  api_group = "Clinical"
  auth = "tutor"
  input {
    json payload
  }
  stack {
    function.run "Clinical/validate" {
      input = {
        kind: "booking", payload: $input.payload, current_time: "now"
      }
    } as $valid
    var $booking {
      value = $valid.value
    }
    function.run "Clinical/assert_owner" {
      input = {
        pet_id: $booking.pet_id, tutor_id: $auth.id
      }
    } as $owned
    db.query veterinario_especie {
      where = $db.veterinario_especie.veterinario_id == $booking.veterinario_id && $db.veterinario_especie.especie_id == $owned.especie_id
      output = ["id"]
      return = {
        type: "single"
      }
    } as $compatible
    precondition ($compatible != null) {
      error_type = "inputerror"
      error = "O profissional não atende a espécie selecionada."
    }
    var $operation_key {
      value = "booking:"|concat:$auth.id|concat:":"|concat:$booking.operacao
    }
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        // Zero is a technical sentinel, never a pet: serializes reservation creation.
        db.add clinical_lock {
          data = {pet_id: 0}
        } as $booking_guard
        db.add clinical_lock {
          data = {
            pet_id: $owned.id
          }
        } as $clinical_guard
        db.query consulta {
          where = $db.consulta.operacao_chave == $operation_key
          output = ["id", "status", "operacao_hash"]
          return = {
            type: "single"
          }
        } as $existing
        conditional {
          if ($existing != null) {
            precondition ($existing.operacao_hash == $valid.signature) {
              error_type = "inputerror"
              error = "A operação já foi usada com dados diferentes."
            }
            var.update $reply {
              value = {
                id: $existing.id, status: $existing.status
              }
            }
          }
          else {
            precondition ($valid.future) {
              error_type = "inputerror"
              error = "Escolha data e horário futuros."
            }
            db.query consulta {
              where = $db.consulta.agendada_para == $booking.agendada_para && ($db.consulta.veterinario_id == $booking.veterinario_id || $db.consulta.pet_id == $owned.id)
              output = ["id"]
              return = {type: "single"}
            } as $slot_conflict
            precondition ($slot_conflict == null) {
              error_type = "inputerror"
              error = "Este horário já está reservado para o pet ou profissional. Escolha outro horário."
            }
            db.add consulta {
              data = {
                pet_id: $owned.id, veterinario_id: $booking.veterinario_id, motivo: $booking.motivo, status: "agendada", agendada_para: $booking.agendada_para, fuso: $booking.fuso, versao: 0, operacao_chave: $operation_key, operacao_hash: $valid.signature
              }
            } as $new_consult
            db.query acesso_autorizado {
              where = $db.acesso_autorizado.pet_id == $owned.id && $db.acesso_autorizado.veterinario_id == $booking.veterinario_id
              return = {
                type: "single"
              }
            } as $consent
            conditional {
              if ($consent == null) {
                db.add acesso_autorizado {
                  data = {
                    pet_id: $owned.id, veterinario_id: $booking.veterinario_id, status: "ativo", concedido_em: "now", revogado_em: null, consulta_origem_id: $new_consult.id
                  }
                } as $granted
              }
              else {
                db.edit acesso_autorizado {
                  field_name = "id"
                  field_value = $consent.id
                  data = {
                    pet_id: $owned.id, veterinario_id: $booking.veterinario_id, status: "ativo", concedido_em: "now", revogado_em: null, consulta_origem_id: $new_consult.id
                  }
                } as $reactivated
              }
            }
            function.run "Clinical/audit" {
              input = {
                pet_id: $owned.id, veterinario_id: $booking.veterinario_id, tutor_id: $auth.id, consulta_id: $new_consult.id, acao: "consentimento_agendamento", operacao: $operation_key
              }
            } as $booking_audit
            var.update $reply {
              value = {
                id: $new_consult.id, status: $new_consult.status
              }
            }
          }
        }
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
        db.del clinical_lock {
          field_name = "id"
          field_value = $booking_guard.id
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "xLL7eeWq_Ct8rJ1iZgkx9LNzf4U"
}
