// Diagnóstico temporário privado; atua somente nas fixtures com prefixo rígido .invalid.
function "Notifications/welcome_synthetic_probe" {
  input {
    email email
    text action?="inspect"
  }
  stack {
    precondition ("/^welcome-[a-f0-9]+-(tutor|vet)@example[.]invalid$/"|regex_matches:$input.email) {
      error_type="inputerror"
      error="Somente fixture sintética."
    }
    precondition ($input.action == "inspect" || $input.action == "prepare" || $input.action == "cleanup") {
      error_type="inputerror"
      error="Ação inválida."
    }
    db.get tutor {
      field_name="email"
      field_value=$input.email
      output=["id", "nome"]
    } as $person
    var $profile {value="tutor"}
    conditional {
      if ($person == null) {
        db.get veterinario {
          field_name="email"
          field_value=$input.email
          output=["id", "nome"]
        } as $person
        var.update $profile {value="veterinario"}
      }
    }
    var $result {value={exists:false}}
    conditional {
      if ($person != null) {
        precondition ($person.nome == "Welcome Test Tutor" || $person.nome == "Welcome Test Vet") {
          error_type="inputerror"
          error="Nome de fixture inesperado."
        }
        var $key {value=$profile ~ ":" ~ ($person.id|to_text)}
        db.get welcome_email_event {
          field_name="key"
          field_value=$key
        } as $event
        var $state {value="pendente"}
        var $attempt {value=null}
        conditional {
          if ($event != null) {
            db.get welcome_email_attempt {
              field_name="event_id"
              field_value=$event.id
            } as $attempt
            conditional {
              if ($attempt != null) {
                var.update $state {value=$attempt.state}
              }
            }
          }
        }
        var.update $result {value={exists:true, profile:$profile, identity_id:$person.id, event_id:$event.id, state:$state}}
        conditional {
          if ($input.action == "prepare") {
            precondition ($event != null && $attempt != null && $attempt.state != "aceito") {
              error_type="inputerror"
              error="Fixture não pronta para concorrência simulada."
            }
            db.del welcome_email_attempt {
              field_name="id"
              field_value=$attempt.id
            }
            var.update $result {value={exists:true, event_id:$event.id, prepared:true}}
          }
          elseif ($input.action == "cleanup") {
            db.transaction {
              stack {
                conditional {
                  if ($attempt != null) {
                    db.del welcome_email_attempt {
                      field_name="id"
                      field_value=$attempt.id
                    }
                  }
                }
                conditional {
                  if ($event != null) {
                    db.del welcome_email_event {
                      field_name="id"
                      field_value=$event.id
                    }
                  }
                }
                conditional {
                  if ($profile == "veterinario") {
                    db.bulk.delete veterinario_especie {
                      where=$db.veterinario_especie.veterinario_id == $person.id
                    }
                    db.bulk.delete veterinario_especialidade {
                      where=$db.veterinario_especialidade.veterinario_id == $person.id
                    }
                    db.del veterinario {
                      field_name="id"
                      field_value=$person.id
                    }
                  }
                  else {
                    db.del tutor {
                      field_name="id"
                      field_value=$person.id
                    }
                  }
                }
                db.del reserva_email {
                  field_name="email"
                  field_value=$input.email
                }
              }
            }
            var.update $result {value={exists:false, cleaned:true}}
          }
        }
      }
    }
  }
  response=$result
  history=false
}
