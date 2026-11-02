# Spec Delta

## ADDED Requirements

### Requirement: Filtros temporais e de estado da lista médica
A lista de Consultas SHALL filtrar no backend antes da paginação, usando o dia do agendamento em America/Sao_Paulo. Hoje SHALL mostrar somente hoje; Próximas SHALL incluir hoje e os quatro dias seguintes. Pendentes, Hoje e Próximas SHALL aceitar apenas agendada/em_atendimento. Concluídas SHALL aceitar somente finalizada e Canceladas somente cancelada, sem limite de cinco dias. Busca e filtro de estado SHALL restringir o resultado da aba.

#### Scenario: Janela de cinco dias incluindo hoje
- **WHEN** o médico seleciona Próximas em 02/11/2026
- **THEN** recebe consultas ativas agendadas de 02/11/2026 a 06/11/2026 inclusive, sem 01/11 ou 07/11, independentemente da quantidade de consultas

#### Scenario: Hoje e pendências anteriores
- **WHEN** o médico alterna entre Hoje e Pendentes
- **THEN** Hoje contém somente consultas ativas do dia local atual e Pendentes inclui também ativas atrasadas e futuras

#### Scenario: Estados encerrados
- **WHEN** o médico seleciona Concluídas ou Canceladas
- **THEN** recebe apenas finalizadas ou canceladas, respectivamente, sem misturar consultas ativas e sem oferecer início/retomada

#### Scenario: Limite de dia no fuso correto
- **WHEN** um agendamento ocorre próximo à meia-noite UTC ou a janela cruza mês/ano
- **THEN** o filtro considera sua data civil em America/Sao_Paulo e mantém exatamente cinco dias em Próximas

#### Scenario: Filtros combinados e paginação
- **WHEN** o médico altera aba, busca, estado ou página
- **THEN** o backend combina as restrições antes de paginar, informa o total real, e uma alteração de filtro retorna à página 1 e limpa o resumo selecionado

#### Scenario: Autorização dos resultados
- **GIVEN** uma consulta pertence a outro profissional ou o consentimento do pet foi revogado
- **WHEN** os filtros ou a busca são aplicados
- **THEN** a consulta de outro profissional não é retornada, e dados privados do pet sem consentimento não são expostos nem usados na busca; a leitura explícita de histórico continua autorizada e auditada

#### Scenario: Contrato remoto anterior
- **WHEN** o backend não confirma a janela e os filtros solicitados
- **THEN** a interface informa indisponibilidade e não apresenta uma lista antiga como se estivesse corretamente filtrada

### Requirement: Agrupamento diário com divisórias legíveis
A lista de cada aba de Consultas SHALL agrupar os registros carregados pela data local do agendamento, com dias e horários em ordem crescente. As divisórias SHALL usar Hoje — DD/MM/AAAA e Amanhã — DD/MM/AAAA quando correspondentes, inclusive em Próximas, e somente DD/MM/AAAA nos demais dias. Cada registro SHALL aparecer uma única vez na página. Dias sem registros SHALL NOT gerar divisórias vazias.

#### Scenario: Hoje, amanhã e outros dias
- **WHEN** a página contém consultas de hoje, amanhã e de um terceiro dia
- **THEN** são exibidos três grupos, usando os rótulos relativos nos dois primeiros e somente a data no terceiro

#### Scenario: Dia dividido entre páginas
- **WHEN** consultas do mesmo dia excedem o limite de uma página
- **THEN** cada página mantém sua divisória correta sem perder registros ou limitar a aba a cinco consultas, preservando o total de resultados

#### Scenario: Lista vazia ou com erro
- **WHEN** a leitura falha ou não encontra resultados
- **THEN** os estados existentes de erro, carregamento e vazio permanecem distintos e não há divisórias sem consultas
