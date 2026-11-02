query "veterinario/agenda" verb=GET {
  api_group = "Clinical"
  auth = "veterinario"
  input {
    text? dia?
    int page?=1
    text? aba?
    text? busca?
    text? estado?
  }
  stack {
    db.query consulta {
      where = $db.consulta.veterinario_id == $auth.id && $db.consulta.status != null
      output = ["id", "pet_id", "veterinario_id", "status", "agendada_para", "motivo"]
      sort = {
        consulta.agendada_para: "asc"
      }
      return = {
        type: "list"
      }
    } as $reservations
    db.query acesso_autorizado {
      where = $db.acesso_autorizado.veterinario_id == $auth.id && $db.acesso_autorizado.status == "ativo"
      output = ["pet_id"]
      return = {
        type: "list"
      }
    } as $consents
    db.query pet {
      join = {
        acesso_autorizado: {
          table: "acesso_autorizado"
          type: "inner"
          where: $db.pet.id == $db.acesso_autorizado.pet_id
        }
      }
      where = $db.acesso_autorizado.veterinario_id == $auth.id && $db.acesso_autorizado.status == "ativo"
      output = ["id", "nome", "foto"]
      return = {
        type: "list"
      }
    } as $pets
    api.lambda {
      code = "const day=$input.dia||null;\nif(day&&!/^\\d{4}-\\d{2}-\\d{2}$/.test(day)) return {error:'Data inválida.'};\nconst page=Number($input.page||1);if(!Number.isInteger(page)||page<1)return {error:'Página inválida.'};\nconst tab=$input.aba||'', search=($input.busca||'').trim().toLocaleLowerCase('pt-BR'), state=$input.estado||'';\nif(tab&&!['Pendentes','Hoje','Próximas','Concluídas','Canceladas'].includes(tab))return {error:'Aba inválida.'};\nif(state&&!['agendada','em_atendimento','finalizada','cancelada'].includes(state))return {error:'Estado inválido.'};\nconst granted=new Set($var.consents.map(x=>x.pet_id));\nconst names=new Map($var.pets.map(x=>[x.id,x]));\nconst fmt=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'});\nconst today=fmt.format(new Date());\nconst rows=$var.reservations.filter(x=>{\n const date=(day||tab==='Hoje'||tab==='Próximas')?fmt.format(new Date(x.agendada_para)):'';\n if(day&&date!==day)return false;\n if(tab==='Canceladas'){if(x.status!=='cancelada')return false;}\n else if(tab==='Concluídas'){if(x.status!=='finalizada')return false;}\n else if((!day||tab)&&['finalizada','cancelada'].includes(x.status))return false;\n if(tab==='Hoje'&&date!==today)return false;\n if(tab==='Próximas'&&date<=today)return false;\n if(state&&x.status!==state)return false;\n if(search&&(!granted.has(x.pet_id)||!(names.get(x.pet_id)?.nome||'').toLocaleLowerCase('pt-BR').includes(search)))return false;\n return true;\n});\nreturn {error:null,contrato_consultas:2,items:rows.slice((page-1)*25,page*25).map(r=>granted.has(r.pet_id)?{...r,pet_nome:names.get(r.pet_id)?.nome||'Pet',pet_foto:names.get(r.pet_id)?.foto??null,autorizado:true}:{id:r.id,status:r.status,agendada_para:r.agendada_para,autorizado:false}),page,total:rows.length};"
      timeout = 5
    } as $listing
    precondition ($listing.error == null) {
      error_type = "inputerror"
      error = "Data ou página inválida."
    }
  }
  response = $listing
  tags = ["vettech", "clinical"]
  guid = "sYrvOSp2XK88WIfOHNUoCJQ1xq4"
}
