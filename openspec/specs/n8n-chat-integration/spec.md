# n8n-chat-integration Specification

## Purpose

Transportar mensagens do assistente ao n8n pelo servidor com credenciais protegidas, contrato validado e isolamento de conversas e sessões.

## Requirements

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

### Requirement: Solicitação estruturada de atendimento humano
O serviço do bot SHALL poder devolver uma intenção estruturada opcional de encaminhamento veterinário associada à resposta válida da conversa corrente. O servidor SHALL validar origem, contrato e correlação com sessão/conversa antes de disponibilizar a confirmação ao tutor. Texto livre SHALL NOT ser interpretado como comando para criar chamado.

#### Scenario: Bot propõe encaminhamento
- **WHEN** chega resposta válida com intenção estruturada reconhecida de encaminhamento
- **THEN** o tutor pode confirmar o chamado com pet e consentimento de compartilhamento, sem criação antecipada

#### Scenario: Resposta comum do workflow atual
- **WHEN** chega resposta válida sem intenção de encaminhamento
- **THEN** a conversa com o bot continua com o contrato e tratamento de erros existentes

#### Scenario: Texto menciona um veterinário
- **WHEN** o bot apenas escreve que recomenda falar com um veterinário
- **THEN** essa frase não cria chamado nem constitui consentimento do tutor

#### Scenario: Intenção inválida ou resposta atrasada
- **WHEN** o sinal estruturado é inválido ou pertence a sessão/conversa já invalidada
- **THEN** ele não habilita confirmação nem cria chamado e segue o tratamento de falhas ou descarte correspondente

### Requirement: Encaminhamento exige contexto autenticado
O sistema SHALL aceitar confirmação de encaminhamento somente de tutor autenticado, usando identidade e conversa verificadas no servidor. Sinais do bot, IDs ou perfis enviados pelo navegador SHALL NOT substituir a validação de propriedade do pet e do contexto compartilhado.

#### Scenario: Visitante ou perfil veterinário
- **GIVEN** o solicitante é visitante ou está autenticado como veterinário
- **WHEN** recebe ou tenta confirmar intenção de encaminhamento
- **THEN** não cria chamado como tutor; ao visitante é informado que precisa entrar como tutor e reiniciar o contexto autenticado

#### Scenario: Contexto forjado
- **GIVEN** o cliente envia identidade, pet ou histórico que não correspondem à conversa confirmada no servidor
- **WHEN** tenta abrir chamado
- **THEN** o backend rejeita sem compartilhar o conteúdo indicado pelo cliente

### Requirement: Bot deixa de responder no atendimento humano
O sistema SHALL interromper a participação automática do bot na conversa encaminhada depois da criação confirmada do chamado. Resposta pendente do bot SHALL NOT ser inserida como mensagem no chamado; mensagens posteriores do atendimento SHALL ter autoria humana ou de evento operacional explícita.

#### Scenario: Chamado aguardando ou em atendimento
- **WHEN** o chamado já foi criado e uma resposta tardia do bot chega
- **THEN** ela não altera o contexto confirmado, não responde ao tutor no chamado e não interfere na conversa humana

#### Scenario: Confirmação falha
- **WHEN** a criação do chamado não foi confirmada
- **THEN** o sistema não anuncia transferência concluída e permite verificar ou repetir a operação sem duplicação
