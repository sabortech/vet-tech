query "adoption" verb=GET {
  api_group = "Pet"
  auth = "tutor"

  input {
  }

  stack {
    db.get tutor {
      field_name = "id"
      field_value = $auth.id
      output = ["id"]
    } as $tutor

    precondition ($tutor != null) {
      error_type = "accessdenied"
      error = "Tutor não autenticado."
    }

    db.query pet {
      join = {
        especie: {
          table: "especie"
          type: "left"
          where: $db.pet.especie_id == $db.especie.id
        }
        raca: {
          table: "raca"
          type: "left"
          where: $db.pet.raca_id == $db.raca.id
        }
      }
      eval = {
        especie_nome: $db.especie.nome
        raca_nome: $db.raca.nome
      }
      where = $db.pet.disponivel_adocao == true
      sort = {pet.created_at: "desc"}
      output = [
        "id"
        "nome"
        "sexo"
        "data_nasc"
        "peso_atual"
        "foto"
        "especie_nome"
        "raca_nome"
      ]
      return = {type: "list"}
    } as $pets

    db.query vacina {
      join = {
        pet: {
          table: "pet"
          where: $db.vacina.pet_id == $db.pet.id
        }
        consulta: {
          table: "consulta"
          type: "left"
          where: $db.vacina.consulta_id == $db.consulta.id
        }
      }
      where = $db.pet.disponivel_adocao == true && ($db.vacina.consulta_id == null || $db.consulta.status == "finalizada" || $db.consulta.status == null || $db.consulta.status == "")
      sort = {vacina.data_aplicacao: "desc"}
      output = ["id", "pet_id", "vacina", "data_aplicacao", "data_prox_dose"]
      return = {type: "list"}
    } as $vaccines

    db.query medicamento {
      join = {
        pet: {
          table: "pet"
          where: $db.medicamento.pet_id == $db.pet.id
        }
        consulta: {
          table: "consulta"
          type: "left"
          where: $db.medicamento.consulta_id == $db.consulta.id
        }
      }
      where = $db.pet.disponivel_adocao == true && ($db.medicamento.consulta_id == null || $db.consulta.status == "finalizada" || $db.consulta.status == null || $db.consulta.status == "")
      sort = {medicamento.data_inicio: "desc"}
      output = [
        "id"
        "pet_id"
        "nome"
        "dose"
        "unidade"
        "frequencia"
        "tipo"
        "data_inicio"
        "data_fim"
      ]
      return = {type: "list"}
    } as $medications

    db.query pet_doenca {
      join = {
        pet: {
          table: "pet"
          where: $db.pet_doenca.pet_id == $db.pet.id
        }
        doenca: {
          table: "doenca"
          type: "left"
          where: $db.pet_doenca.doenca_id == $db.doenca.id
        }
        consulta_doenca: {
          table: "consulta_doenca"
          where: $db.pet_doenca.consulta_doenca_id == $db.consulta_doenca.id
        }
        consulta: {
          table: "consulta"
          type: "left"
          where: $db.consulta_doenca.consulta_id == $db.consulta.id
        }
      }
      eval = {
        nome: $db.doenca.nome
      }
      where = $db.pet.disponivel_adocao == true && $db.pet_doenca.estado != "curada" && ($db.consulta.status == "finalizada" || $db.consulta.status == null || $db.consulta.status == "")
      sort = {pet_doenca.data_evolucao: "desc"}
      output = ["id", "pet_id", "estado", "nome"]
      return = {type: "list"}
    } as $conditions

    db.query exame {
      join = {
        pet: {
          table: "pet"
          where: $db.exame.pet_id == $db.pet.id
        }
        consulta: {
          table: "consulta"
          type: "left"
          where: $db.exame.consulta_id == $db.consulta.id
        }
      }
      where = $db.pet.disponivel_adocao == true && ($db.exame.consulta_id == null || $db.consulta.status == "finalizada" || $db.consulta.status == null || $db.consulta.status == "")
      sort = {exame.data_realizacao: "desc"}
      output = ["id", "pet_id", "tipo", "status", "data", "data_solicitacao", "data_realizacao"]
      return = {type: "list"}
    } as $exams

    var $today {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    api.lambda {
      code = """
        const byPet=(rows,id)=>rows.filter(row=>String(row.pet_id)===String(id));
        const latest=(rows,dateFields)=>{
          const value=row=>dateFields.map(field=>row[field]).find(Boolean)||'';
          return rows.slice().sort((a,b)=>value(b).localeCompare(value(a)))[0]||null;
        };
        return $var.pets.map(pet=>{
          const petVaccines=byPet($var.vaccines,pet.id).filter(row=>row.vacina);
          const vaccine=latest(
            petVaccines.filter(row=>row.data_aplicacao),
            ['data_aplicacao']
          )||latest(
            petVaccines.filter(row=>row.data_prox_dose),
            ['data_prox_dose']
          );
          const medications=byPet($var.medications,pet.id).filter(row=>
            row.data_inicio&&row.data_inicio<=$var.today&&
            (!row.data_fim||row.data_fim>=$var.today)
          );
          const conditions=byPet($var.conditions,pet.id)
            .filter(row=>['ativa','em_tratamento','controlada'].includes(row.estado))
            .map(row=>({
            nome:row.nome||'Condição clínica',
            estado:row.estado
          }));
          const exam=latest(
            byPet($var.exams,pet.id).filter(row=>
              row.tipo&&['solicitado','realizado'].includes(row.status)&&
              (row.data_realizacao||row.data||row.data_solicitacao)
            ),
            ['data_realizacao','data','data_solicitacao']
          );
          return {
            ...pet,
            vacina:vaccine?{
              nome:vaccine.vacina,
              data_aplicacao:vaccine.data_aplicacao,
              data_prox_dose:vaccine.data_prox_dose
            }:null,
            medicamentos:medications.map(row=>({
              nome:row.nome,
              dose:row.dose,
              unidade:row.unidade,
              frequencia:row.frequencia,
              tipo:row.tipo,
              data_inicio:row.data_inicio,
              data_fim:row.data_fim
            })),
            doencas:conditions,
            exame:exam?{
              tipo:exam.tipo,
              data:exam.data_realizacao||exam.data||exam.data_solicitacao,
              estado:exam.status
            }:null
          };
        });
        """
      timeout = 5
    } as $adoption_pets
  }

  response = $adoption_pets
  tags = ["vettech"]
  guid = "-vIWWTSw1x4BR0BF5jNWG8dkExs"
}
