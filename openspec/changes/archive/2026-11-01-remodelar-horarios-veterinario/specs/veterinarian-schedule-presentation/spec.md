# Spec Delta

## Purpose
Apresentar os agendamentos do veterinário em uma agenda visual consistente com o Vet Tech, permitindo localizar pets e iniciar os fluxos clínicos existentes com segurança.

## ADDED Requirements

### Requirement: Menu veterinário consistente e restrito
O sistema SHALL usar a apresentação lateral compartilhada, com recolhimento desktop, drawer móvel e somente Horários e Consultas como destinos veterinários implementados, identificando a seção ativa e mantendo identidade e logout acessíveis.

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
