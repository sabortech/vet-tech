## ADDED Requirements

### Requirement: Seletor de data em painel personalizado
O sistema SHALL apresentar somente um botão Hoje e um botão com ícone de calendário como controles de seleção, sem campo de data visível. O ícone SHALL ter nome acessível e abrir um diálogo amplo nas cores do sistema, com mês/ano em português, navegação mensal/anual e dias selecionáveis. A tartaruga decorativa SHALL usar asset existente e não impedir a interação. O diálogo SHALL adaptar-se ao celular e tema escuro, permitir fechamento por Escape, manter foco dentro enquanto aberto e devolver foco ao ícone quando fechado.

#### Scenario: Abrir e navegar sem alterar a agenda
- **WHEN** o veterinário abre o calendário e navega por meses/anos
- **THEN** o painel inicia no mês da data ativa e a agenda permanece no dia original até uma seleção explícita

#### Scenario: Escolher dia no painel
- **WHEN** o veterinário seleciona um dia válido, passado ou futuro, no calendário
- **THEN** o painel fecha, a agenda mostra esse dia e a paginação volta a 1 usando o carregamento e permissões existentes

#### Scenario: Fechar sem selecionar
- **WHEN** o veterinário fecha pelo botão, clique externo ou Escape
- **THEN** a data permanece a mesma e o foco retorna ao botão com ícone de calendário

#### Scenario: Voltar para hoje
- **WHEN** o veterinário aciona Hoje
- **THEN** a agenda carrega o dia atual em America/Sao_Paulo sem criar ou modificar consultas

### Requirement: Luz verde apenas na janela aberta
O sistema SHALL apresentar um brilho verde animado percorrendo somente as bordas da janela aberta no sentido horário. Hoje e o ícone de calendário SHALL NOT receber esse efeito. A animação SHALL respeitar preferência por movimento reduzido e não bloquear conteúdo ou cliques.

#### Scenario: Janela aberta
- **WHEN** o calendário está aberto
- **THEN** a borda da janela mostra a luz verde no sentido horário e seus controles permanecem utilizáveis

#### Scenario: Movimento reduzido
- **WHEN** o navegador solicita movimento reduzido
- **THEN** a borda mantém destaque estático sem rotação
