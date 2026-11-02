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

### Requirement: Histórico com cabeçalho de perfil do paciente
O rótulo do cabeçalho SHALL ser “Perfil do pet”. O histórico anterior SHALL apresentar retrato circular em destaque, nome, sexo, nascimento, peso informado e contagens reais de consultas, vacinas, medicamentos, doenças e exames antes das categorias. SHALL adaptar o cabeçalho a celular e aos temas existentes, preservando mascote, dados, rolagem, fechamento, foco, falha/nova tentativa e rascunho.

#### Scenario: Dados autorizados do perfil
- **GIVEN** o médico tem autorização ativa para o pet
- **WHEN** abre o histórico
- **THEN** a leitura é validada e auditada pelo backend e o perfil apresenta somente dados e contagens daquele pet, com foto disponível ou patinha

#### Scenario: Resposta antiga ou acesso revogado
- **GIVEN** a seleção/sessão mudou ou o consentimento foi revogado
- **WHEN** uma leitura falha ou uma resposta antiga chega
- **THEN** nenhum retrato ou dado do pet anterior é restaurado

#### Scenario: Foto ausente ou falha
- **WHEN** não há foto válida ou a imagem não carrega
- **THEN** o perfil usa patinha somente para foto nula/vazia e indica foto indisponível para imagem existente com erro, sem imagem artificial e sem afetar as demais informações

### Requirement: Foto consistente em todas as apresentações médicas do paciente
O sistema SHALL exibir a foto cadastrada e autorizada do paciente na agenda, lista de consultas, resumo, atendimento e histórico. Resumo e atendimento SHALL priorizar a foto da leitura clínica atual e aceitar a foto da agenda do mesmo pet como compatibilidade após leitura autorizada bem-sucedida. A patinha SHALL aparecer somente para foto nula/vazia. Foto existente com erro SHALL indicar falha de exibição, sem patinha.

#### Scenario: Foto atual disponível
- **GIVEN** o veterinário tem autorização ativa para o paciente
- **WHEN** abre resumo, atendimento ou histórico e a leitura clínica retorna foto válida
- **THEN** a foto atual é exibida mesmo se a agenda não tiver foto ou tiver uma anterior, preservando autorização e auditoria no backend

#### Scenario: Contrato anterior sem foto
- **GIVEN** a leitura clínica autorizada e auditada foi concluída e omite o campo foto (contrato anterior)
- **WHEN** existe foto válida na agenda autorizada do mesmo paciente na sessão atual
- **THEN** a apresentação usa essa foto e nunca a de outro paciente

#### Scenario: Foto nula no banco
- **WHEN** o banco retorna foto nula/vazia, mesmo havendo foto antiga na agenda
- **THEN** a apresentação usa patinha e mantém dados e ações existentes

#### Scenario: Falha de imagem existente
- **WHEN** existe foto no banco mas seu formato é inválido ou seu carregamento falha
- **THEN** a apresentação informa falha de imagem sem usar patinha

#### Scenario: Falha, revogação e resposta antiga
- **GIVEN** mudou o paciente ou a sessão, ou o backend negou a leitura
- **WHEN** chega resposta antiga ou ocorre falha de autorização
- **THEN** nenhum retrato do contexto anterior é restaurado e a falha permanece explícita

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
