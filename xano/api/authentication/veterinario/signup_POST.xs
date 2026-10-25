query "veterinario/signup" verb=POST {
  api_group = "Authentication"

  input {
    text nome filters=trim
    email email filters=trim|lower
    text telefone filters=trim
    password password
    text crmv filters=trim|upper
    text crmv_uf filters=trim|upper
    int clinica_id?
    int[] especies_ids
    int[] especialidades_ids
  }

  stack {
    precondition ($input.nome != "" && $input.telefone != "" && $input.password != "") {
      error_type = "inputerror"
      error = "Preencha todos os campos obrigatórios."
    }

    precondition ("/^[A-Z0-9]{1,20}$/"|regex_matches:$input.crmv) {
      error_type = "inputerror"
      error = "CRMV deve conter de 1 a 20 letras ou números, sem espaços internos."
    }

    precondition ("/^(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)$/"|regex_matches:$input.crmv_uf) {
      error_type = "inputerror"
      error = "Informe uma UF válida para o CRMV."
    }

    var $species {
      value = $input.especies_ids|unique
    }

    var $specialties {
      value = $input.especialidades_ids|unique
    }

    precondition (($species|count) > 0 && ($specialties|count) > 0) {
      error_type = "inputerror"
      error = "Selecione pelo menos uma espécie e uma especialidade."
    }

    conditional {
      if ($input.clinica_id != null && $input.clinica_id != 0) {
        db.has clinica {
          field_name = "id"
          field_value = $input.clinica_id
        } as $has_clinic

        precondition ($has_clinic) {
          error_type = "inputerror"
          error = "Clínica indisponível."
        }
      }
    }

    foreach ($species) {
      each as $species_id {
        db.has especie {
          field_name = "id"
          field_value = $species_id
        } as $exists

        precondition ($exists) {
          error_type = "inputerror"
          error = "Espécie indisponível."
        }
      }
    }

    foreach ($specialties) {
      each as $specialty_id {
        db.has especialidade {
          field_name = "id"
          field_value = $specialty_id
        } as $exists

        precondition ($exists) {
          error_type = "inputerror"
          error = "Especialidade indisponível."
        }
      }
    }

    function.run "Identity/check_email_available" {
      input = {email: $input.email}
    } as $email_check

    db.transaction {
      stack {
        db.add reserva_email {
          data = {email: $input.email, perfil: "veterinario"}
        } as $reservation

        db.add veterinario {
          data = {
            nome      : $input.nome
            email     : $input.email
            telefone  : $input.telefone
            senha     : $input.password
            crmv      : $input.crmv
            crmv_uf   : $input.crmv_uf
            clinica_id: $input.clinica_id
          }
        } as $vet

        foreach ($species) {
          each as $species_id {
            db.add veterinario_especie {
              data = {veterinario_id: $vet.id, especie_id: $species_id}
            } as $species_link
          }
        }

        foreach ($specialties) {
          each as $specialty_id {
            db.add veterinario_especialidade {
              data = {veterinario_id: $vet.id, especialidade_id: $specialty_id}
            } as $specialty_link
          }
        }

        db.edit reserva_email {
          field_name = "id"
          field_value = $reservation.id
          data = {identidade_id: $vet.id}
        } as $complete
      }
    }
  }

  response = {success: true}
  tags = ["vettech"]
  guid = "IvZWoi43BQXpjoGEnI3rgEm-U_c"
}
