## ADDED Requirements
### Requirement: Transporte privado e contrato validado
O backend SHALL enviar POST HTTPS ao webhook configurado com segredo e token Xano apenas nos cabeçalhos, timeout total de 60 segundos, sem redirecionamentos nem retries automáticos. SHALL validar IDs, ok, reply e error e retornar falha genérica para rede, JSON inválido ou falha de configuração, sem expor segredos.
#### Scenario: Visitante
- **WHEN** visitante envia pergunta
- **THEN** o n8n recebe authenticated false, role visitante, name null e nenhum cabeçalho de token Xano
#### Scenario: Pessoa autenticada
- **WHEN** pessoa autenticada envia pergunta
- **THEN** token e identidade vêm do State no servidor, e não de dados de usuário enviados pelo navegador
#### Scenario: Erro de credencial do webhook
- **WHEN** chega 401/403 sem contrato válido
- **THEN** o chat mostra erro genérico sem expirar a sessão Xano
### Requirement: Contexto isolado e resposta assíncrona
O sistema SHALL gerar IDs por conversa e mensagem, enviar histórico anterior limitado a 20 mensagens/20 mil caracteres sem duplicar a atual, permitir somente uma pergunta pendente por conversa e descartar resposta depois de fechamento, nova conversa ou mudança de sessão. A espera SHALL manter fechamento e histórico acessíveis.
#### Scenario: Nova conversa
- **WHEN** a pessoa fecha e abre o chat
- **THEN** há novo conversation_id e contexto n8n vazio, preservando separadamente o histórico visual da aba
#### Scenario: Resposta atrasada
- **WHEN** uma resposta antiga chega após nova conversa ou logout
- **THEN** não aparece nem modifica a nova sessão
### Requirement: Falhas e retomada
O sistema SHALL mostrar reply válido como texto seguro, oferecer tentativa manual em falhas sem duplicar a pergunta e solicitar novo login em SESSION_INVALID do contrato. Não SHALL fingir resposta de IA usando respostas locais prontas.
#### Scenario: Timeout
- **WHEN** o webhook não responde no prazo
- **THEN** aparece Não consegui responder agora. Tente novamente. com tentativa manual
