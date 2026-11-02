# Design

## Context
Ver proposal.md. SettingsState usa endpoints tutor/account e tutor/password, exclui veterinário e guarda cache por token. O modelo médico possui nome, telefone, email, crmv/crmv_uf e senha; não possui CPF/endereço. A sidebar médica usa ações locais para Horários e Consultas. preferences.js intercepta links com edição pendente e encaminha o destino exato por controles ocultos.

## Goals / Non-Goals
Reutilizar a página e o estado existentes sem duplicar formulários; adicionar somente contratos médicos de conta. Não alterar cadastro, dados profissionais protegidos, prontuário, permissões clínicas ou backend do tutor.

## Decisions
- Contexto de SettingsState inclui token, perfil, identidade e geração de sessão; cada operação captura e revalida esse contexto, mantendo leitura background sem bloqueio de navegação.
- Campos e rascunho por perfil: tutor mantém nome/telefone/endereço e CPF mascarado; médico salva apenas nome/telefone e exibe CRMV/UF bloqueados. Mesmo componente account/security/preferences, com sidebar apropriada.
- Três endpoints Xano aditivos, autenticação veterinario e auth.id; allowlist sem IDs de cliente. Senha utiliza o campo médico senha e security.check_password. Sem migração de banco.
- Menu médico nas configurações usa links `/?secao=horarios` e `/?secao=consultas`, permitindo ao guard preservar o destino. A entrada da área médica aplica a intenção antes do carregamento e mantém ações locais existentes na agenda.
- Configurações usa a mesma rota e o mesmo mecanismo de descarte, preferências e logout; somente destinos permitidos por perfil são executados.

## Risks / Trade-offs
- Regredir tutor → manter contratos e testes anteriores, adicionar cenários médicos e de substituição de perfil.
- Resposta atrasada → comparar contexto capturado antes de aplicar resultado/limpar flags.
- Endpoint novo exige publicação → validar fontes com parser, preparar/publicar somente os três novos documentos, registrar diferença entre testes locais e integração real.
- Credenciais reais → integração usa somente fixtures explicitamente sintéticas de desenvolvimento; nunca trocar senha da conta do usuário.

## Migration Plan
Publicação aditiva de três endpoints sem tabelas/records/env. Frontend e menu após validações. Rollback remove acesso e endpoints novos sem apagar dados ou desfazer senhas alteradas. Não publicar arquivos de outras mudanças pendentes.
