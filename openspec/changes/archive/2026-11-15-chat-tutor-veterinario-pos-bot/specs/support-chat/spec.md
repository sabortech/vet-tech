# Continuidade do suporte

## MODIFIED Requirements

### Requirement: Conversa local honesta
O sistema SHALL aceitar mensagens e chips, exibir digitação e respostas do serviço n8n por transporte privado no backend sem inventar dados clínicos, usar conteúdo textual seguro e iniciar conversa limpa com o bot ao reabrir, arquivando interações no histórico local da aba. SHALL NOT simular respostas de IA com respostas locais prontas. Para chamados humanos confirmados, SHALL recuperar a conversa persistente solicitada pelo participante autenticado, sem substituir mensagens humanas por respostas do n8n nem reiniciar o atendimento.

#### Scenario: Perguntar sobre vacina
- **WHEN** a pessoa pergunta a data de uma vacina
- **THEN** o chat orienta consultar Vacinas no prontuário sem fornecer datas inventadas

#### Scenario: Falha de resposta
- **WHEN** o processamento da resposta falha
- **THEN** aparece mensagem de erro com Tentar de novo sem duplicar a pergunta

#### Scenario: Retomar atendimento veterinário
- **WHEN** o participante autenticado solicita retomar um chamado confirmado
- **THEN** o sistema recupera mensagens e estado autorizados daquele chamado e identifica o pet e o veterinário responsável quando atribuído

### Requirement: Saudação e histórico isolados
O sistema SHALL iniciar conversa nova com o bot a cada abertura, saudando pelo nome confirmado se autenticado e genericamente se visitante. SHALL cancelar respostas pendentes no fechamento e permitir histórico temporário somente leitura dentro do painel, limitado às últimas 20 conversas com interação na aba. SHALL apagar histórico temporário e conversa local ao mudar sessão ou recarregar, sem expor tokens nem misturar usuários. Chamados humanos confirmados SHALL persistir no backend, podendo ser retomados ou consultados separadamente pelo participante após nova validação de acesso, sem limite derivado do arquivo temporário do bot.

#### Scenario: Reabrir e consultar histórico
- **WHEN** a pessoa envia mensagem somente ao bot, fecha e abre o chat
- **THEN** aparece saudação nova sem mensagens anteriores, acessíveis pelo botão Histórico com retorno à conversa atual

#### Scenario: Trocar sessão
- **WHEN** ocorre login, logout ou troca de identidade
- **THEN** conversa e histórico locais são apagados e a saudação reflete o novo nome ou visitante
- **AND** nenhum chamado é carregado sem verificar participação da identidade atual

#### Scenario: Fechar durante digitação
- **WHEN** o chat é fechado com resposta pendente do bot
- **THEN** essa resposta não aparece na próxima conversa

#### Scenario: Fechar chamado humano
- **WHEN** o tutor fecha o chat ou recarrega durante atendimento humano
- **THEN** o chamado não é encerrado e suas mensagens confirmadas permanecem recuperáveis mediante autenticação e autorização

## ADDED Requirements

### Requirement: Distinção entre assistente e atendimento veterinário
O sistema SHALL informar se a conversa está com o bot, aguardando veterinário, em atendimento humano ou encerrada. A criação de chamado SHALL exigir confirmação do pet e compartilhamento da conversa. A assunção SHALL identificar nome e CRMV/UF do profissional, sem apresentar o bot como veterinário ou prometer resolução clínica automática.

#### Scenario: Tutor acompanha transição
- **WHEN** o encaminhamento é confirmado e depois assumido por um veterinário
- **THEN** o tutor acompanha os estados aguardando e em atendimento, identifica o profissional e pode conversar diretamente com ele

#### Scenario: Sem confirmação
- **WHEN** o bot sugere encaminhamento mas o tutor não confirma
- **THEN** a conversa continua identificada como assistente, sem chamado criado
