# tutor-dashboard Specification

## Purpose

Oferecer ao tutor uma visão resumida dos dados já registrados para seus pets, com escopo geral ou individual, para facilitar a identificação de eventos e o acesso às áreas existentes sem substituir o prontuário.

## Requirements

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

### Requirement: Dashboard individual reúne informações em um único cartão
Ao escolher qualquer pet, o Dashboard SHALL reunir identificação, indicadores, próximo evento, acompanhamentos, atividade recente e ações em um único cartão com seções internas. O contorno individual e a sombra SHALL seguir a mesma cor da barra de prazo da próxima dose: verde, amarelo, âmbar ou vermelho. Sem data o LED SHALL ficar apagado e a sombra SHALL usar o tom neutro da barra, sem indicar estado clínico positivo por decoração. A visão geral SHALL manter sua sombra anterior e contorno apagado quando não houver data. Dados, ações, loading e erros SHALL permanecer inalterados e o layout SHALL adaptar-se aos dois temas e celular.

#### Scenario: Abrir Dashboard de outro pet
- **WHEN** o tutor escolhe qualquer pet no filtro individual
- **THEN** todas as informações disponíveis ficam no mesmo cartão, com LED de seu próprio status e ações vinculadas ao pet escolhido

### Requirement: Listagem usa card completo inspirado na Jessy
O Dashboard SHALL apresentar todos os pets da visão geral com o mesmo modelo completo inspirado no card da Jessy do protótipo: superfície branca, bordas arredondadas, sombra suave, foto retangular à esquerda, nome marrom destacado, identificação, três indicadores bege, faixa de vacinas, acompanhamento detalhado e ações. Os indicadores SHALL representar peso cadastrado, próxima vacina registrada e última consulta finalizada. O acompanhamento SHALL apresentar a mensagem dos registros consultados, a prévia de itens quando houver e o próximo evento registrado. Os textos SHALL usar português brasileiro. Ausências SHALL ser explícitas, sem inventar dados, unidades ou conclusões clínicas.

#### Scenario: Vários pets com o mesmo modelo
- **WHEN** o tutor abre a visão geral com vários pets
- **THEN** todos os cartões apresentam a mesma estrutura completa, inclusive “Acompanhamento detalhado”
- **AND** cada cartão oferece “Ver Dashboard do pet”, “Agendar consulta”, “Vacinas” e “Prontuário” para o respectivo pet, preservando as regras existentes de contexto das ações

#### Scenario: Dados incompletos ou foto indisponível
- **WHEN** um pet não tem foto acessível, peso, próxima dose ou consulta finalizada
- **THEN** seu cartão conserva a estrutura e apresenta imagem substituta ou mensagens de ausência nos campos correspondentes
- **AND** nomes longos e mensagens extensas não encobrem informações ou ações

### Requirement: Faixa de vacinas é fiel aos registros disponíveis
O card SHALL apresentar uma faixa horizontal com LED de prazo e detalhe decorativo de tartaruga, acompanhada de texto derivado dos registros disponíveis de próxima dose. A faixa SHALL NOT representar percentual de imunização, declarar vacinação completa ou classificar cuidados como pendentes com base apenas na falta de registros. Decorações SHALL ser ignoradas por tecnologia assistiva e o texto SHALL transmitir a informação sem depender de cores.

#### Scenario: Próxima dose disponível
- **WHEN** existe próxima dose registrada no resumo
- **THEN** o cartão informa nome e data disponíveis junto à faixa visual, mantendo a distinção existente para datas registradas ultrapassadas
- **AND** não apresenta porcentagem de cobertura vacinal

#### Scenario: Não há próxima dose registrada
- **WHEN** não existe próxima dose informada
- **THEN** o cartão informa essa ausência sem afirmar que a vacinação está completa ou atrasada

### Requirement: Dashboard reproduz fundo e composição responsiva do protótipo
O Dashboard SHALL usar a imagem `fundopets.jpeg` existente como fundo da área principal, com sua textura bege e estampas visíveis ao redor dos cards. A visão geral SHALL organizar os cards em duas colunas quando a largura útil comportar sua leitura e em uma coluna nas demais telas. Foto, indicadores, acompanhamento e ações SHALL se reorganizar em telas estreitas sem rolagem horizontal ou sobreposição. O filtro de escopo e a navegação compartilhada SHALL continuar acessíveis. A aplicação SHALL manter contraste legível no tema claro e escuro e evitar que mascote ou chat impeçam o acesso aos cards.

#### Scenario: Desktop com espaço suficiente
- **WHEN** o tutor acessa o Dashboard em desktop com área útil suficiente para duas colunas
- **THEN** os cards aparecem lado a lado, alinhados pelo topo, com espaçamento entre linhas e fundo visível
- **AND** cartões mais altos não se sobrepõem aos seguintes

#### Scenario: Celular ou navegação expandida
- **WHEN** a largura útil diminui, inclusive por abertura da navegação
- **THEN** a listagem se adapta para uma coluna conforme necessário e mantém textos e ações acessíveis
- **AND** não existe rolagem horizontal na página

#### Scenario: Carregamento, erro e lista vazia
- **WHEN** os dados estão carregando, uma leitura falha ou o tutor não possui pets
- **THEN** o Dashboard conserva o fundo e apresenta o estado correspondente, incluindo nova tentativa ou cadastro quando aplicável
- **AND** falha não é apresentada como ausência de itens de acompanhamento

### Requirement: Barra de vacina indica o prazo registrado e abre Vacinas
A barra SHALL indicar o prazo da próxima dose futura mais próxima; se não houver dose futura, SHALL usar a data ultrapassada mais recente. Mais de sete dias SHALL usar LED verde suave, de um a sete dias amarelo, hoje âmbar, data ultrapassada vermelho suave e ausência de data válida LED apagado. O texto SHALL informar os dias, incluindo singular e plural, ou ausência de próxima dose. Datas ultrapassadas SHALL orientar a conferência dos registros sem afirmar que a vacina não foi aplicada. O nome e a data de referência SHALL estar disponíveis ao usuário. O indicador SHALL ser acionável por mouse e teclado e abrir Vacinas do pet correspondente, sem representar percentual ou piscar.

#### Scenario: Limites de prazo
- **WHEN** a data prevista é hoje, em um, sete ou oito dias
- **THEN** o indicador usa respectivamente âmbar, amarelo, amarelo ou verde, com texto do prazo correto

#### Scenario: Histórico sem dose futura
- **WHEN** só há datas previstas ultrapassadas válidas
- **THEN** o indicador vermelho usa a mais recente e informa “Data prevista há N dias — confira os registros”, ajustando o singular

#### Scenario: Dados insuficientes
- **WHEN** não existe data prevista válida
- **THEN** o LED fica apagado com “Sem próxima dose registrada”, sem inferir situação vacinal

#### Scenario: Abrir vacinas pelo indicador
- **WHEN** o tutor aciona a barra com clique, Enter ou Espaço
- **THEN** navega para Vacinas do pet do card, mantendo as validações existentes de propriedade no backend

### Requirement: Legenda das cores da barra de vacina
A barra SHALL exibir uma legenda ao receber hover ou foco por teclado, explicando verde (mais de sete dias), amarelo (um a sete dias), âmbar (hoje), vermelho (data ultrapassada, conferir registros) e apagado (sem próxima dose registrada). Os nomes das cores SHALL aparecer em negrito e na respectiva cor, com cinza para o estado apagado e contraste legível. A legenda SHALL esclarecer que data ultrapassada não confirma ausência de aplicação e que o clique abre Vacinas do pet.

#### Scenario: Consultar significado das cores
- **WHEN** o tutor posiciona o mouse ou foca a barra pelo teclado
- **THEN** a legenda apresenta todas as cinco situações com seus significados e mantém a ação de abrir Vacinas

### Requirement: Carregamento do Dashboard não bloqueia outras ações
O Dashboard SHALL executar leituras remotas sem bloquear a navegação da sessão. Ações repetidas para o mesmo escopo enquanto a leitura estiver em andamento SHALL NOT iniciar outro lote. A troca de escopo e o logout SHALL invalidar respostas anteriores. As leituras SHALL manter validação de propriedade, no máximo quatro chamadas concorrentes, estados de erro e nova tentativa, sem cache clínico entre sessões.

#### Scenario: API lenta com navegação disponível
- **WHEN** a API dos resumos demora para responder
- **THEN** o tutor continua podendo abrir/recolher o menu ou navegar, com carregamento explícito

#### Scenario: Resposta anterior chega depois da troca de escopo
- **WHEN** uma leitura antiga termina após troca de escopo ou logout
- **THEN** seus dados e erros não substituem o contexto atual

### Requirement: Cards da mesma linha têm altura uniforme
Os cards da visão geral SHALL ocupar a mesma altura na respectiva linha e alinhar os botões na base, preservando todo o conteúdo. Em uma coluna SHALL manter altura natural.

#### Scenario: Resumos com quantidades diferentes de acompanhamento
- **WHEN** dois cards da mesma linha têm conteúdos de tamanhos diferentes
- **THEN** suas bordas inferiores e ações ficam alinhadas, sem truncar o maior conteúdo

### Requirement: Contorno do card acompanha a cor do prazo vacinal
O card SHALL apresentar um segmento de LED percorrendo seu contorno em sentido horário, usando a mesma cor do indicador de prazo da vacina. O LED SHALL permanecer apagado sem data válida, não interceptar cliques ou foco e não substituir a explicação textual do indicador. Com preferência por movimento reduzido, o segmento SHALL continuar girando mais lentamente, como o LED da área do veterinário, conforme solicitação explícita do usuário.

#### Scenario: Pet com prazo registrado
- **WHEN** o card apresenta um indicador verde, amarelo, âmbar ou vermelho
- **THEN** o segmento luminoso percorre o contorno em sentido horário com a mesma cor

#### Scenario: Sem data e movimento reduzido
- **WHEN** não há data registrada ou a preferência de movimento reduzido está ativa
- **THEN** o LED respectivamente fica apagado ou gira mais lentamente na cor do indicador

### Requirement: Dashboard mostra resumos progressivamente e evita releituras imediatas
O Dashboard SHALL apresentar cada resumo válido assim que a leitura terminar, mantendo a ordem dos pets e uma indicação de carregamento enquanto houver leituras pendentes. Uma leitura concluída com sucesso SHALL poder ser reaproveitada por até 15 segundos na mesma sessão, desde que a lista de pets e o dia local permaneçam iguais. Logout e ações para abrir dados clínicos ou agendamento SHALL invalidar o reaproveitamento. O botão Atualizar SHALL buscar os dados novamente independentemente do prazo. Falhas SHALL continuar explícitas e não representar ausência de cuidados.

#### Scenario: Um pet demora mais que os demais
- **WHEN** uma leitura termina enquanto outra permanece aguardando
- **THEN** o resumo concluído aparece sem aguardar o restante e a tela informa que ainda está carregando

#### Scenario: Retorno imediato ao Dashboard
- **WHEN** o tutor retorna em até 15 segundos após sucesso e o contexto não mudou
- **THEN** os dados já obtidos aparecem sem repetir as leituras remotas

#### Scenario: Atualização explícita ou dados expirados
- **WHEN** o tutor aciona Atualizar ou o contexto, dia ou prazo mudou
- **THEN** novas leituras autorizadas são executadas, sem compartilhar dados entre sessões

### Requirement: Barra apresenta luz percorrendo o prazo em loop
A barra SHALL apresentar um reflexo luminoso percorrendo sua extensão do início ao fim, reiniciando no começo a cada ciclo sem voltar, usando exclusivamente a cor do status no segmento luminoso e sem representar percentual de carregamento ou vacinação. A decoração SHALL ignorar interações e não gerar consultas ou eventos remotos. Sem próxima dose registrada, SHALL permanecer apagada; movimento reduzido SHALL tornar o efeito mais lento.

#### Scenario: Barra com data registrada
- **WHEN** o card tem prazo vacinal conhecido
- **THEN** uma luz percorre a barra repetidamente sem alterar seu significado ou impedir o acesso a Vacinas

### Requirement: Legenda identifica a situação atual do card
A legenda SHALL mostrar “Situação atual:” seguida do nome da cor correspondente ao status real do indicador daquele pet, em negrito e na respectiva cor.

#### Scenario: Consultar situação do pet
- **WHEN** o tutor abre a legenda de um card
- **THEN** a situação atual mostra Verde, Amarelo, Âmbar, Vermelho ou Apagado conforme a barra daquele pet

### Requirement: Moldura da foto tem sombra forte conforme o status
A foto ou imagem substituta de cada card SHALL apresentar uma sombra forte na cor da situação da barra, com contorno marcado, halo colorido e tom cinza sem data registrada. O efeito SHALL preservar dimensões, cantos e interações, sem animação adicional.

#### Scenario: Situação do pet refletida na foto
- **WHEN** o card apresenta uma situação de prazo vacinal
- **THEN** a moldura da foto acompanha a mesma cor em uma sombra forte

### Requirement: Cabeçalho segue a hierarquia de Consultas
O Dashboard SHALL apresentar título e descrição, botão Atualizar verde sólido e filtro Mostrar em barra separada com superfície adaptada ao tema. SHALL preservar seleção geral/individual e agendamento condicional, com quebra responsiva sem sobreposição.

#### Scenario: Acessar e filtrar o Dashboard
- **WHEN** o tutor acessa o Dashboard e seleciona um pet
- **THEN** o topo mantém título, descrição e Atualizar, com filtro e agendamento na barra abaixo

### Requirement: Peso cadastrado apresentado em quilogramas
O sistema SHALL apresentar o peso cadastrado com a unidade Kg, mantendo o valor registrado e usando “Não informado” quando ausente. Zero SHALL ser exibido como “0 Kg”. A convenção Kg SHALL ser explícita no cadastro e nas exibições do Dashboard e Prontuário; não haverá conversão ou alteração de valores armazenados.

#### Scenario: Peso disponível
- **WHEN** o pet possui peso cadastrado 5
- **THEN** o campo de peso exibe “5 Kg”

#### Scenario: Peso ausente
- **WHEN** o peso não foi informado
- **THEN** o campo exibe “Não informado” sem sufixo Kg
