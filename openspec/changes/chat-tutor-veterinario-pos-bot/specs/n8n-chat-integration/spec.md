# Encaminhamento do assistente

## ADDED Requirements

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
