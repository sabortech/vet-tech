# veterinarian-schedule-presentation Specification

## Purpose
Apresentar os agendamentos do veterinário em uma agenda visual consistente com o Vet Tech, permitindo localizar pets e iniciar os fluxos clínicos existentes com segurança.

## Requirements

### Requirement: Menu veterinário consistente e restrito
O sistema SHALL usar a apresentação lateral compartilhada, com recolhimento desktop, drawer móvel e somente Horários, Consultas e Configurações como destinos veterinários implementados, identificando a seção ativa e mantendo identidade e logout acessíveis.

#### Scenario: Navegação veterinária
- **WHEN** o veterinário alterna entre Horários e Consultas ou recolhe o menu
- **THEN** vê o mesmo padrão verde do sistema, sem opções exclusivas do tutor, e mantém acesso às duas seções e à saída

### Requirement: Seleção de dia e apresentação fiel dos horários
O sistema SHALL apresentar data em português, navegação entre dias, semana selecionável, calendário e Hoje. A linha do tempo SHALL posicionar cards pela hora local America/Sao_Paulo, incluir consultas fora da faixa padrão 08–17 e empilhar consultas da mesma hora sem sobreposição nem duração presumida.

#### Scenario: Alterar dia
- **WHEN** o veterinário seleciona outro dia ou Hoje
- **THEN** a página volta a 1 e carrega apenas a agenda do dia escolhido, mantendo atualização e paginação

#### Scenario: Horários incomuns e simultâneos
- **WHEN** há consultas às 07:30, 10:15, 10:45 ou 19:00
- **THEN** todas são alcançáveis na hora correspondente e os cards não se sobrepõem

### Requirement: Cards com dados autorizados e ações existentes
O sistema SHALL apresentar nome, foto disponível com alternativa neutra, motivo, hora e estado legível. SHALL preservar início/retomada e histórico; finalizadas SHALL NOT oferecer início. O backend SHALL fornecer foto/nome/motivo somente para consultas do profissional e pets com autorização ativa (RF03/RF04, RN01–RN08).

#### Scenario: Foto disponível
- **GIVEN** a consulta é do veterinário e há consentimento ativo
- **WHEN** a agenda retorna foto do pet
- **THEN** o card a apresenta com o nome e as ações autorizadas

#### Scenario: Consentimento revogado
- **GIVEN** o tutor revogou o consentimento
- **WHEN** o veterinário carrega a agenda
- **THEN** o backend omite dados privados e o card informa a revogação sem foto, motivo ou ações clínicas

#### Scenario: Atendimento existente
- **WHEN** o veterinário começa, retoma ou consulta histórico pelo card
- **THEN** executa o fluxo existente com autorização e auditoria mantidas no backend

### Requirement: Resumo e estados honestos e responsivos
O sistema SHALL distinguir carregamento, falha e vazio, adaptar cards e controles ao celular e respeitar tokens de tema. Resumos SHALL indicar quando se referem à página atual. A agenda SHALL NOT afirmar horários livres ou duração sem contrato de disponibilidade.

#### Scenario: Agenda paginada
- **WHEN** há mais de 25 consultas no dia
- **THEN** o total representa o dia e os indicadores derivados dos cards são identificados como referentes à página atual

#### Scenario: Falha de leitura
- **WHEN** a consulta da agenda falha
- **THEN** a mensagem de erro e atualização permanecem disponíveis sem anunciar agenda vazia ou horários livres

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
O sistema SHALL apresentar um brilho verde animado percorrendo somente as bordas da janela aberta no sentido horário. Hoje e o ícone de calendário SHALL NOT receber esse efeito. A animação SHALL ser contínua, linear e suave, sem bloquear conteúdo ou cliques. Quando houver preferência por movimento reduzido, SHALL usar velocidade menor mantendo o traço em circulação conforme solicitado pelo usuário.

#### Scenario: Janela aberta
- **WHEN** o calendário está aberto
- **THEN** a borda da janela mostra a luz verde no sentido horário e seus controles permanecem utilizáveis

#### Scenario: Movimento reduzido
- **WHEN** o navegador solicita movimento reduzido
- **THEN** o segmento continua circulando no sentido horário em velocidade menor, sem transformar toda a borda em luz estática

### Requirement: Seletores de mês e ano com abertura inferior
O sistema SHALL apresentar seletores de mês e ano no diálogo do calendário com cores e cantos do sistema e chevron apontado para baixo. As opções SHALL abrir somente abaixo do acionador, com altura limitada e rolagem interna; SHALL preservar operação por teclado, seleção ativa e adaptação aos temas claro/escuro e ao celular.

#### Scenario: Abrir lista de mês ou ano
- **WHEN** o veterinário aciona um dos seletores
- **THEN** a lista aparece abaixo do controle, sem reposicionamento para cima, e permite alcançar as opções por rolagem e teclado

#### Scenario: Selecionar opção
- **WHEN** o veterinário escolhe mês ou ano
- **THEN** a grade mensal atualiza sem alterar a data da agenda antes da seleção explícita de um dia
