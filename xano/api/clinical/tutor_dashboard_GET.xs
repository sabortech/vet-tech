query "tutor/dashboard" verb=GET {
  api_group = "Clinical"
  auth = "tutor"

  input {
    int pet_id
  }

  stack {
    var $today {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
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
      where = $db.pet.id == $input.pet_id && $db.pet.tutor_id == $auth.id
      output = ["id", "nome", "raca_id", "data_nasc", "peso_atual", "foto", "especie_nome", "raca_nome"]
      return = {
        type: "single"
      }
    } as $owned_pet
    precondition ($owned_pet != null) {
      error_type = "notfound"
      error = "Pet não disponível."
    }
    db.query consulta {
      join = {
        pet: {
          table: "pet"
          where: $db.consulta.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.consulta.pet_id == $owned_pet.id && $db.consulta.status == "agendada" && $db.consulta.agendada_para >= now
      sort = {
        consulta.agendada_para: "asc"
      }
      output = ["id", "pet_id", "status", "agendada_para"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 1
        }
      }
    } as $next_consultations
    db.query consulta {
      join = {
        pet: {
          table: "pet"
          where: $db.consulta.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.consulta.pet_id == $owned_pet.id && $db.consulta.retorno_previsto >= $today
      sort = {
        consulta.retorno_previsto: "asc"
      }
      output = ["id", "pet_id", "status", "retorno_previsto"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 1
        }
      }
    } as $next_returns
    db.query consulta {
      join = {
        pet: {
          table: "pet"
          where: $db.consulta.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.consulta.pet_id == $owned_pet.id && $db.consulta.retorno_previsto < $today
      sort = {
        consulta.retorno_previsto: "desc"
      }
      output = ["id", "pet_id", "status", "retorno_previsto"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 11
        }
      }
    } as $overdue_returns
    db.query consulta {
      join = {
        pet: {
          table: "pet"
          where: $db.consulta.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.consulta.pet_id == $owned_pet.id && $db.consulta.status == "finalizada" && $db.consulta.data_atendimento != null
      sort = {
        consulta.data_atendimento: "desc"
      }
      output = ["id", "pet_id", "status", "data_atendimento"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 3
        }
      }
    } as $recent_attended_consultations
    db.query consulta {
      join = {
        pet: {
          table: "pet"
          where: $db.consulta.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.consulta.pet_id == $owned_pet.id && $db.consulta.status == "finalizada" && $db.consulta.data_atendimento == null && $db.consulta.data != null
      sort = {
        consulta.data: "desc"
      }
      output = ["id", "pet_id", "status", "data"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 3
        }
      }
    } as $recent_legacy_consultations
    db.query vacina {
      join = {
        pet: {
          table: "pet"
          where: $db.vacina.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.vacina.pet_id == $owned_pet.id && $db.vacina.data_prox_dose >= $today
      sort = {
        vacina.data_prox_dose: "asc"
      }
      output = ["id", "pet_id", "vacina", "data_prox_dose"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 1
        }
      }
    } as $next_vaccines
    db.query vacina {
      join = {
        pet: {
          table: "pet"
          where: $db.vacina.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.vacina.pet_id == $owned_pet.id && $db.vacina.data_prox_dose < $today
      sort = {
        vacina.data_prox_dose: "desc"
      }
      output = ["id", "pet_id", "vacina", "data_prox_dose"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 11
        }
      }
    } as $overdue_vaccines
    db.query vacina {
      join = {
        pet: {
          table: "pet"
          where: $db.vacina.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.vacina.pet_id == $owned_pet.id && $db.vacina.data_aplicacao != null
      sort = {
        vacina.data_aplicacao: "desc"
      }
      output = ["id", "pet_id", "vacina", "data_aplicacao"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 3
        }
      }
    } as $recent_vaccines
    db.query exame {
      join = {
        pet: {
          table: "pet"
          where: $db.exame.pet_id == $db.pet.id
        }
      }
      where = $db.pet.tutor_id == $auth.id && $db.exame.pet_id == $owned_pet.id && $db.exame.status == "solicitado" && $db.exame.data_realizacao == null
      sort = {
        exame.data_solicitacao: "desc"
      }
      output = ["id", "pet_id", "tipo", "status", "data_solicitacao"]
      return = {
        type: "list"
        paging: {
          page: 1
          per_page: 11
        }
      }
    } as $pending_exams
    api.lambda {
      code = """
        const mergeById=(...groups)=>{
          const rows=new Map();
          for(const group of groups)for(const row of group)rows.set(String(row.id),row);
          return [...rows.values()];
        };
        const limited=(rows)=>rows.slice(0,10);
        const consultations=mergeById($var.next_consultations,$var.next_returns,limited($var.overdue_returns),$var.recent_attended_consultations,$var.recent_legacy_consultations);
        const vaccines=mergeById($var.next_vaccines,limited($var.overdue_vaccines),$var.recent_vaccines);
        return {
          ...$var.owned_pet,
          consultas:consultations.map(({id,pet_id,...row})=>row),
          vacinas:vaccines.map(({id,pet_id,...row})=>row),
          exames:limited($var.pending_exams).map(({id,pet_id,...row})=>row),
          acompanhamentos_truncados:$var.overdue_returns.length>10||$var.overdue_vaccines.length>10||$var.pending_exams.length>10
        };
        """
      timeout = 5
    } as $dashboard
  }

  response = $dashboard
  tags = ["vettech", "clinical"]
  guid = "Av1-BKAsLi94Y4Ah3IHokZmhS78"
}
