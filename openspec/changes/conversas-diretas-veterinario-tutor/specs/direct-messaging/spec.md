## Purpose
Permitir conversas simples e privadas iniciadas por veterinário com tutor cadastrado, separadas do fluxo de atendimento e sem liberar acesso clínico.

## ADDED Requirements

### Requirement: Início por veterinário com tutor cadastrado
Veterinário autenticado SHALL acessar Falar com tutor no chat, abrir seletor pesquisável de todos os tutores e iniciar/retomar conversa com o selecionado. A busca SHALL limitar campos a identificador/nome e paginar resultados, sem request por tecla. O backend SHALL verificar perfil e existência do tutor; Tutor autenticado SHALL pesquisar veterinários e iniciar conversa simples com o profissional selecionado, validando sua existência e derivando a identidade do tutor do token.

#### Scenario: Escolher tutor
- **GIVEN** o usuário autenticado é veterinário
- **WHEN** pesquisa e confirma um tutor cadastrado
- **THEN** abre conversa privada com ele sem criar atendimento, consulta ou vínculo clínico

### Requirement: Caixa de conversas por participante
Os dois perfis SHALL acessar Conversas e listar somente os próprios pares, com nome confirmado e indicação de mensagens não vistas. O tutor SHALL conseguir responder aos profissionais que iniciaram conversa com ele. A fila de atendimentos SHALL permanecer separada.

#### Scenario: Tutor responde
- **GIVEN** um veterinário iniciou conversa com o tutor
- **WHEN** o tutor abre Conversas
- **THEN** encontra o profissional, abre o histórico e responde na mesma conversa

### Requirement: Privacidade e persistência
O backend SHALL permitir leitura e escrita somente ao tutor e veterinário do par, derivando identidade do token e revalidando participação em todas as operações. O par SHALL ser único e sua criação idempotente mesmo em concorrência. Não SHALL expor prontuário, CPF, endereço, credenciais, outros pares ou contexto do assistente.

#### Scenario: Terceiro tenta acessar
- **GIVEN** a conversa pertence a outro tutor ou profissional
- **WHEN** o usuário tenta ler, enviar, confirmar leitura ou alterar mensagem
- **THEN** o backend nega sem retornar conteúdo

### Requirement: Compositor compartilhado e alterações seguras
Conversas simples SHALL reutilizar emojis, nomes por participante, recibos Entregue/Visto e menu de edição/exclusão próprias em até 10 minutos do envio original, com autoria, revisão, retry idempotente e auditoria privada no backend. Não SHALL apresentar assunção, encerramento ou status de atendimento. A conversa SHALL persistir ao fechar e reabrir.

#### Scenario: Mensagem e reabertura
- **WHEN** um participante envia mensagem e reabre a conversa
- **THEN** o texto persistido continua no histórico com recibos e regras de alteração preservados

### Requirement: Consumo controlado
Pesquisa e listas SHALL atualizar por ação explícita; apenas conversa aberta SHALL usar polling, suspenso em aba oculta ou painel fechado. Leituras SHALL ser agrupadas e respostas de sessão anterior descartadas. Não SHALL chamar n8n para mensagens diretas nem enviar notificações externas.

#### Scenario: Fechar conversa
- **WHEN** o chat fecha ou muda sessão
- **THEN** polling para e respostas antigas não aparecem no novo contexto
