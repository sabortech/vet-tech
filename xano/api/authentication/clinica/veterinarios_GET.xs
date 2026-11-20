query "clinica/veterinarios" verb=GET {
  api_group = "Authentication"
  auth = "clinica_admin"

  input {
  }

  stack {
    db.get clinica_admin {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "clinica_id", "ativo"]
    } as $admin

    precondition ($admin != null && $admin.ativo == true && $admin.clinica_id != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }

    db.get clinica {
      field_name = "id"
      field_value = $admin.clinica_id
      output = ["id"]
    } as $clinica

    precondition ($clinica != null) {
      error_type = "accessdenied"
      error = "Sessão inválida."
    }

    db.query veterinario {
      where = $db.veterinario.clinica_id == $clinica.id
      output = ["id", "nome", "crmv", "crmv_uf", "especialidade"]
      return = {type: "list"}
    } as $veterinarios

    db.query veterinario_especialidade {
      join = {
        veterinario: {
          table: "veterinario"
          where: $db.veterinario_especialidade.veterinario_id == $db.veterinario.id
        }
        especialidade: {
          table: "especialidade"
          where: $db.veterinario_especialidade.especialidade_id == $db.especialidade.id
        }
      }
      where = $db.veterinario.clinica_id == $clinica.id
      eval = {nome: $db.especialidade.nome}
      output = ["veterinario_id", "nome"]
      return = {type: "list"}
    } as $especialidades

    api.lambda {
      code = """
        return $var.veterinarios.map(v => ({
          id: v.id,
          nome: v.nome,
          crmv: v.crmv,
          crmv_uf: v.crmv_uf,
          especialidades: (() => {
            const nomes = $var.especialidades.filter(e => e.veterinario_id === v.id).map(e => e.nome).filter(Boolean);
            return nomes.length ? nomes : (v.especialidade ? [v.especialidade] : []);
          })()
        }));
        """
      timeout = 5
    } as $resultado
  }

  response = $resultado
  tags = ["vettech"]
}
