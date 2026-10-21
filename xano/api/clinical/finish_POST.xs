query "veterinario/consultas/{consulta_id}/finalizar" verb=POST {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    int consulta_id
    int versao
    json payload
  }
  stack {
    function.run "Clinical/assert_consultation" {
      input = {
        consulta_id: $input.consulta_id, veterinario_id: $auth.id
      }
    } as $consult
    function.run "Clinical/validate" {
      input = {
        kind: "finalize", payload: $input.payload, current_time: "now"
      }
    } as $valid
    var $reply {
      value = null
    }
    db.transaction {
      stack {
        db.add clinical_lock {
          data = {
            pet_id: $consult.pet_id
          }
        } as $clinical_guard
        function.run "Clinical/assert_consultation" {
          input = {
            consulta_id: $input.consulta_id, veterinario_id: $auth.id
          }
        } as $consult
        function.run "Clinical/assert_access" {
          input = {
            pet_id: $consult.pet_id, veterinario_id: $auth.id
          }
        } as $authorized
        conditional {
          if ($consult.status == "finalizada") {
            var.update $reply {
              value = {
                id: $consult.id, status: "finalizada", versao: $consult.versao
              }
            }
          }
          else {
            precondition ($consult.status == "em_atendimento") {
              error_type = "inputerror"
              error = "Consulta não está em atendimento."
            }
            precondition ($consult.versao == $input.versao) {
              error_type = "inputerror"
              error = "A consulta foi alterada em outra sessão. Atualize antes de finalizar."
            }
            var $record {
              value = $valid.value
            }
            foreach ($record.vacinas) {
              each as $line {
                db.add vacina {
                  data = {
                    pet_id: $consult.pet_id, veterinario_id: $auth.id, consulta_id: $consult.id, origem_linha: $line.linha_id, vacina: $line.vacina, lote: $line.lote, data_aplicacao: $line.data_aplicacao, data_prox_dose: $line.data_prox_dose
                  }
                } as $published_line
              }
            }
            foreach ($record.medicamentos) {
              each as $line {
                db.add medicamento {
                  data = {
                    pet_id: $consult.pet_id, veterinario_id: $auth.id, consulta_id: $consult.id, origem_linha: $line.linha_id, nome: $line.nome, dose: $line.dose, unidade: $line.unidade, frequencia: $line.frequencia, via: $line.via, tipo: $line.tipo, data_inicio: $line.data_inicio, data_fim: $line.data_fim
                  }
                } as $published_line
              }
            }
            foreach ($record.exames) {
              each as $line {
                db.add exame {
                  data = {
                    pet_id: $consult.pet_id, veterinario_id: $auth.id, consulta_id: $consult.id, origem_linha: $line.linha_id, tipo: $line.tipo, status: $line.status, data_solicitacao: $line.data_solicitacao, data_realizacao: $line.data_realizacao, resultado: $line.resultado
                  }
                } as $published_line
              }
            }
            foreach ($record.doencas) {
              each as $line {
                db.get doenca {
                  field_name = "id"
                  field_value = $line.doenca_id
                } as $disease
                precondition ($disease != null) {
                  error_type = "inputerror"
                  error = "Doença não disponível."
                }
                precondition ($disease.pet_id == null || $disease.pet_id == 0) {
                  error_type = "inputerror"
                  error = "Doença não disponível."
                }
                db.add consulta_doenca {
                  data = {
                    consulta_id: $consult.id, pet_id: $consult.pet_id, veterinario_id: $auth.id, doenca_id: $line.doenca_id, origem_linha: $line.linha_id, data_diagnostico: $line.data_diagnostico, estado: $line.estado, observacoes: $line.observacoes, publicado_em: "now"
                  }
                } as $evolution
                db.query pet_doenca {
                  where = $db.pet_doenca.pet_id == $consult.pet_id && $db.pet_doenca.doenca_id == $line.doenca_id
                  return = {
                    type: "single"
                  }
                } as $condition
                conditional {
                  if ($condition == null) {
                    db.add pet_doenca {
                      data = {
                        pet_id: $consult.pet_id, doenca_id: $line.doenca_id, estado: $line.estado, data_evolucao: $line.data_diagnostico, atualizado_em: "now", consulta_doenca_id: $evolution.id, versao: 1
                      }
                    } as $updated_condition
                  }
                  else {
                    conditional {
                      if ($line.data_diagnostico >= $condition.data_evolucao) {
                        db.edit pet_doenca {
                          field_name = "id"
                          field_value = $condition.id
                          data = {
                            estado: $line.estado, data_evolucao: $line.data_diagnostico, atualizado_em: "now", consulta_doenca_id: $evolution.id, versao: $condition.versao + 1
                          }
                        } as $evolved_condition
                      }
                    }
                  }
                }
              }
            }
            db.edit consulta {
              field_name = "id"
              field_value = $consult.id
              data = {
                status: "finalizada", finalizada_em: "now", motivo: $record.motivo, diagnostico: $record.diagnostico, obs: $record.obs, data_atendimento: $record.data_atendimento, retorno_previsto: $record.retorno_previsto, rascunho: null, versao: $consult.versao + 1
              }
            } as $finished
            var $finish_key {
              value = "finalizar:"|concat:$consult.id
            }
            function.run "Clinical/audit" {
              input = {
                pet_id: $consult.pet_id, consulta_id: $consult.id, veterinario_id: $auth.id, acao: "finalizar", operacao: $finish_key
              }
            } as $audit_event
            var.update $reply {
              value = {
                id: $finished.id, status: $finished.status, versao: $finished.versao
              }
            }
          }
        }
        db.del clinical_lock {
          field_name = "id"
          field_value = $clinical_guard.id
        }
      }
    }
  }
  response = $reply
  tags = ["vettech", "clinical"]
  guid = "w1YvCCWISSMzzQMKP9Y-FMN5afM"
}
