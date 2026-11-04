## ADDED Requirements
### Requirement: Painel modal de suporte
O sistema SHALL abrir chat no clique da mascote com backdrop escuro translúcido, identidade do protótipo, boas-vindas, chips, campo e aviso veterinário. Desktop SHALL manter painel acima da mascote; mobile SHALL usar tela cheia.
#### Scenario: Abrir e fechar
- **WHEN** a pessoa ativa a mascote
- **THEN** o modal abre, contém foco e fecha por Esc, clique fora, minimizar ou fechar, restaurando foco
### Requirement: Conversa local honesta
O sistema SHALL aceitar mensagens e chips, exibir digitação e orientações locais sem inventar dados clínicos, usar conteúdo textual seguro e iniciar conversa limpa ao reabrir, arquivando interações no histórico local.
#### Scenario: Perguntar sobre vacina
- **WHEN** a pessoa pergunta a data de uma vacina
- **THEN** o chat orienta consultar Vacinas no prontuário sem fornecer datas inventadas
#### Scenario: Falha de resposta
- **WHEN** o processamento local falha
- **THEN** aparece mensagem de erro com Tentar de novo sem duplicar a pergunta

### Requirement: Mascote ativa durante conversa
Enquanto o chat estiver aberto, a mascote SHALL manter braços em V e luz acesa atrás, sem depender de hover ou foco e sem rastrear o ponteiro. Fechar ou minimizar SHALL restaurar o comportamento normal. Movimento reduzido SHALL preservar pose e luz estáticas.
#### Scenario: Conversar sem apontar a mascote
- **WHEN** o chat abre e o cursor se afasta da mascote
- **THEN** a pose em V e a luz permanecem até o fechamento do painel

### Requirement: Saudação e histórico isolados
O sistema SHALL iniciar conversa nova a cada abertura, saudando pelo nome confirmado se autenticado e genericamente se visitante. SHALL cancelar respostas pendentes no fechamento e permitir histórico somente leitura dentro do painel, limitado às últimas 20 conversas com interação na aba. SHALL apagar histórico e conversa ao mudar sessão ou recarregar, sem expor tokens nem misturar usuários.
#### Scenario: Reabrir e consultar histórico
- **WHEN** a pessoa envia mensagem, fecha e abre o chat
- **THEN** aparece saudação nova sem mensagens anteriores, acessíveis pelo botão Histórico com retorno à conversa atual
#### Scenario: Trocar sessão
- **WHEN** ocorre login, logout ou troca de identidade
- **THEN** conversa e histórico são apagados e a saudação reflete o novo nome ou visitante
#### Scenario: Fechar durante digitação
- **WHEN** o chat é fechado com resposta pendente
- **THEN** essa resposta não aparece na próxima conversa
