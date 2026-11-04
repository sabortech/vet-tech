## Purpose

Oferecer ao tutor uma visão resumida dos dados já registrados para seus pets, com escopo geral ou individual, para facilitar a identificação de eventos e o acesso às áreas existentes sem substituir o prontuário.

## ADDED Requirements

### Requirement: Dashboard do tutor usa escopo geral ou de pet
O sistema SHALL disponibilizar ao tutor autenticado um Dashboard com seletor de escopo contendo “Todos os pets” e cada pet de sua propriedade. O escopo SHALL afetar somente o conteúdo do Dashboard e SHALL NOT selecionar, trocar ou limpar o pet ativo no prontuário.

#### Scenario: Exibir visão geral
- **WHEN** o tutor abre o Dashboard com “Todos os pets” selecionado
- **THEN** o sistema apresenta os pets próprios com resumos e eventos identificados pelo respectivo pet
- **AND** não apresenta pets pertencentes a outros tutores

#### Scenario: Filtrar por pet próprio
- **GIVEN** o tutor possui mais de um pet cadastrado
- **WHEN** seleciona um deles no filtro do Dashboard
- **THEN** o conteúdo passa a resumir somente esse pet
- **AND** a seleção clínica atual permanece inalterada

#### Scenario: Selecionar pet não autorizado
- **GIVEN** o cliente envia ou mantém um identificador de pet que não pertence ao tutor autenticado
- **WHEN** o Dashboard solicita os dados desse pet
- **THEN** o backend nega a leitura e nenhum dado do pet é apresentado

#### Scenario: Tutor sem pets
- **WHEN** o Dashboard geral é aberto e o tutor não possui pets
- **THEN** o sistema informa que não há pets cadastrados e oferece o fluxo existente de cadastro de pet

### Requirement: Leituras clínicas do Dashboard são limitadas por pet
O sistema SHALL solicitar dados clínicos por pet, usando IDs da lista autenticada do tutor; no escopo “Todos os pets”, SHALL carregar cada pet próprio com concorrência limitada, e no escopo individual SHALL solicitar somente o pet selecionado. O backend SHALL validar a propriedade do pet autenticado em cada leitura e SHALL aplicar limites e ordenação específicos para próxima consulta, retorno previsto, próxima dose, registros recentes e itens de acompanhamento, sem usar um limite global de histórico que possa ocultar dados de outro pet. Exames pendentes e datas registradas ultrapassadas SHALL ser apresentados como prévia limitada, com indicação quando existirem mais registros que os exibidos.

#### Scenario: Leitura do escopo geral
- **WHEN** o tutor seleciona “Todos os pets”
- **THEN** o cliente solicita resumos usando somente IDs da lista autenticada de pets
- **AND** cada resposta inclui apenas o perfil e os registros limitados daquele pet
- **AND** chamadas concorrentes são limitadas para evitar uma rajada de requisições

#### Scenario: Leitura de pet individual
- **GIVEN** o tutor selecionou um pet próprio
- **WHEN** o Dashboard atualiza os dados
- **THEN** o cliente envia o `pet_id` selecionado
- **AND** o backend recusa IDs inexistentes ou pertencentes a outro tutor sem retornar dados do pet

#### Scenario: Histórico excede a prévia de acompanhamento
- **GIVEN** existem mais registros de acompanhamento do que o limite exibido
- **WHEN** o Dashboard apresenta a prévia
- **THEN** mantém o indicador de que há itens registrados
- **AND** informa que a lista está limitada, sem sugerir que os registros exibidos sejam o histórico completo

### Requirement: Dashboard apresenta perfil com dados cadastrais existentes
No escopo de um pet, o sistema SHALL apresentar no topo os dados disponíveis do perfil cadastrado: foto quando acessível, nome, espécie, raça e idade calculada a partir da data de nascimento. O peso cadastrado SHALL ser apresentado como valor atual sem inferir unidade ou evolução não armazenada.

#### Scenario: Perfil com dados opcionais ausentes
- **WHEN** foto, raça, data de nascimento ou peso não estiverem cadastrados ou acessíveis
- **THEN** o Dashboard apresenta os demais dados disponíveis sem inventar valores ou substituir ausência por uma afirmação clínica

#### Scenario: Idade calculada a partir do nascimento
- **GIVEN** o pet possui data de nascimento válida
- **WHEN** o Dashboard apresenta o perfil
- **THEN** a idade é calculada usando a data atual e a data cadastrada, sem tratar idade como dado persistido

### Requirement: Dashboard resume datas e registros clínicos disponíveis
O sistema SHALL apresentar, quando existirem nos dados autorizados, a próxima dose de vacina registrada, a consulta finalizada mais recente, o próximo evento datado registrado e uma prévia limitada de consultas e vacinas recentes. O sistema SHALL distinguir consulta agendada, retorno previsto, próxima dose de vacina e exame solicitado; SHALL NOT apresentar exame como compromisso futuro sem uma data futura registrada.

#### Scenario: Apresentar próximo evento registrado
- **GIVEN** há datas futuras em consulta agendada, retorno previsto ou próxima dose de vacina
- **WHEN** o Dashboard resume o pet
- **THEN** apresenta o evento futuro mais próximo com seu tipo e data, sem confundir retorno previsto com consulta agendada

#### Scenario: Não há datas futuras conhecidas
- **WHEN** não há consulta agendada, retorno previsto ou próxima dose futura registrada
- **THEN** o Dashboard informa que não há próximo evento registrado, sem afirmar que o pet não precisa de cuidados

#### Scenario: Resumir exame sem agendamento
- **GIVEN** existe exame solicitado sem realização registrada, sem data futura de execução
- **WHEN** o Dashboard apresenta itens a acompanhar
- **THEN** informa que a realização não está registrada e não classifica o exame como atrasado ou como compromisso futuro

#### Scenario: Histórico recente
- **WHEN** existem consultas finalizadas ou vacinas registradas
- **THEN** o Dashboard apresenta uma prévia curta ordenada pelas datas disponíveis e oferece acesso às seções existentes para consultar o histórico completo

### Requirement: Status do Dashboard descreve somente os registros disponíveis
O sistema SHALL apresentar mensagens de acompanhamento derivadas exclusivamente dos dados clínicos carregados. Uma próxima dose de vacina ou um retorno previsto com data anterior à data atual SHALL ser descrito como data registrada ultrapassada, sem afirmar que o cuidado não ocorreu. Um exame solicitado sem realização registrada SHALL ser descrito como realização não registrada, sem inferir atraso. Na ausência desses itens, o sistema SHALL usar uma mensagem limitada aos registros consultados e SHALL NOT declarar que o pet está saudável, em dia ou sem necessidade de cuidados.

#### Scenario: Data registrada ultrapassada
- **GIVEN** a próxima dose de vacina ou o retorno previsto possui data anterior à data atual
- **WHEN** o Dashboard calcula o resumo
- **THEN** identifica a data registrada como ultrapassada e apresenta o motivo sem afirmar que o evento foi perdido

#### Scenario: Nenhum item de acompanhamento identificado
- **GIVEN** os dados do Dashboard foram carregados com sucesso e não contêm data registrada ultrapassada nem exame solicitado sem realização
- **WHEN** o Dashboard calcula o resumo
- **THEN** informa que nenhum item de acompanhamento foi identificado nos registros consultados
- **AND** não declara que o pet está saudável ou que todos os cuidados estão em dia

#### Scenario: Falha ou dados insuficientes para calcular
- **WHEN** uma leitura necessária falha ou os dados não podem ser confirmados como carregados
- **THEN** o Dashboard apresenta indisponibilidade ou ausência de informação suficiente e permite nova tentativa
- **AND** não apresenta o estado de falha como se não houvesse pendências

### Requirement: Ações rápidas levam a funcionalidades existentes
O Dashboard SHALL oferecer ações para agendar consulta, abrir a seção existente de Vacinas e abrir o prontuário do pet correspondente. No escopo “Todos os pets”, uma ação que exige um pet SHALL identificar e encaminhar o pet escolhido pelo tutor, sem alterar silenciosamente a seleção clínica. O Dashboard SHALL NOT oferecer como funcional um destino que ainda esteja indisponível na interface.

#### Scenario: Agendar para um pet no escopo geral
- **GIVEN** o tutor está no Dashboard “Todos os pets”
- **WHEN** inicia o agendamento a partir de um cartão de pet
- **THEN** o fluxo de agendamento recebe o pet escolhido como contexto da ação
- **AND** nenhuma seleção de prontuário é alterada sem ação explícita do tutor

#### Scenario: Abrir seção clínica do pet
- **GIVEN** o tutor está no Dashboard de um pet
- **WHEN** abre Vacinas ou Prontuário por uma ação rápida
- **THEN** o sistema navega para a funcionalidade existente e valida a propriedade do pet no backend

#### Scenario: Destino ainda indisponível
- **WHEN** uma seção como Exames não está disponível na interface
- **THEN** o Dashboard não apresenta um atalho que sugira que essa seção pode ser aberta
