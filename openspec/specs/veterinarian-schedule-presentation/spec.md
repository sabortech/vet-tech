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

### Requirement: Finalização confirmada retorna à agenda com card concluído
O sistema SHALL apresentar sucesso no canto inferior esquerdo após confirmação do rascunho ou da finalização. Após finalização confirmada, inclusive reconciliação, SHALL abrir Horários no dia do agendamento em America/Sao_Paulo e revalidar a agenda autenticada. O card finalizado SHALL indicar Concluída e não oferecer Retomar/Começar. A consulta SHALL deixar as pendências da seção Consultas. Datas clínicas editadas SHALL NOT mover o agendamento. Autorização e auditoria do backend SHALL ser preservadas.

#### Scenario: Concluir atendimento autorizado
- **GIVEN** a consulta pertence ao veterinário e há autorização ativa do tutor
- **WHEN** a operação de finalização confirma publicação e auditoria pelo backend
- **THEN** a interface notifica sucesso no canto inferior esquerdo e abre o dia agendado em Horários, com card Concluída após a revalidação

#### Scenario: Confirmar finalização após perda da resposta
- **GIVEN** a resposta da finalização foi perdida
- **WHEN** a reconciliação confirma a consulta finalizada
- **THEN** a interface retorna à agenda e notifica sucesso sem repetir a escrita

#### Scenario: Falha ou resposta antiga
- **GIVEN** o salvamento falhou, houve conflito ou a sessão/consulta mudou durante a operação
- **WHEN** a operação termina
- **THEN** não há declaração falsa de sucesso nem redirecionamento para uma consulta anterior

### Requirement: Cards médicos verdes com luz na agenda e foto
O sistema SHALL preservar dados, estados textuais e ações autorizadas nos cards de Horários e Consultas. O acabamento dos cards e da moldura da foto/fallback SHALL seguir a paleta contextual do atendimento: vermelho/agendada, amarelo/em atendimento e verde/finalizada. SHALL apresentar LED verde percorrendo no sentido horário o perímetro da agenda do dia, além do calendário existente; o LED da moldura do pet SHALL acompanhar a cor do status. O trecho iluminado SHALL projetar halo da mesma cor que acompanha somente o segmento móvel, inclusive no calendário e chat, sem iluminar estaticamente toda a borda. O conteúdo SHALL permanecer imóvel, legível e clicável; movimento reduzido SHALL desacelerar a circulação.

#### Scenario: Card em atendimento ou concluído
- **WHEN** a agenda apresenta consultas em atendimento ou finalizadas
- **THEN** o card usa detalhes amarelos para em atendimento ou verdes para finalizadas, com estado textual correspondente e contorno da foto/fallback na mesma cor em circulação

#### Scenario: Agenda e movimento reduzido
- **WHEN** Horários está aberto e o navegador solicita movimento reduzido
- **THEN** a borda da agenda do dia e da moldura do pet continuam circulando em velocidade menor sem bloquear conteúdo ou controles

#### Scenario: Acesso revogado
- **GIVEN** o tutor revogou o acesso
- **WHEN** o card é exibido
- **THEN** foto, nome, motivo e ações privadas permanecem ocultos conforme o backend

### Requirement: Atendimento e painéis acompanham a preferência de tema
O sistema SHALL aplicar a preferência claro/escuro existente ao atendimento, seus campos, estados, histórico, calendário clínico, confirmação de descarte e notificações de gravação. A troca SHALL atualizar painéis e notificações já abertos sem recarregar ou perder o rascunho, preservando contraste, ícones, LED e sua circulação. A preferência salva SHALL continuar sendo aplicada antes da apresentação visível pelo mecanismo já existente.

#### Scenario: Trocar tema com painel aberto
- **GIVEN** há um rascunho local e histórico ou calendário aberto
- **WHEN** a preferência de tema do documento muda
- **THEN** o formulário e o painel acompanham as cores do tema sem alterar valores, seleção ou visibilidade

#### Scenario: Preferência persistida e notificação
- **WHEN** o atendimento é aberto com tema escuro salvo e uma gravação é confirmada
- **THEN** formulário, campos e toast usam superfícies escuras e textos legíveis mantendo identidade verde

### Requirement: Histórico dos cards usa o painel compartilhado
O sistema SHALL abrir o mesmo painel de histórico do atendimento a partir dos cards autorizados em Horários e Consultas, usando o pet daquele card. SHALL incluir carregamento, falha/nova tentativa, vazio, categorias clínicas, tema e mascote. Nova tentativa SHALL manter o mesmo alvo. Fechamento SHALL restaurar foco ao acionador. O histórico SHALL NOT aparecer inline abaixo da agenda nem modificar o atendimento aberto.

#### Scenario: Abrir histórico de outro pet
- **GIVEN** o veterinário possui autorização vigente para o pet do card
- **WHEN** abre seu histórico após ter atendido outro pet, ou repete uma leitura que falhou
- **THEN** o painel solicita o pet do card pelas mesmas APIs autorizadas e auditadas e preserva o rascunho de atendimento

### Requirement: Lista de Consultas baseada no protótipo
O sistema SHALL apresentar abas Pendentes, Hoje, Próximas, Concluídas e Canceladas, busca por pet, filtro por estado, cards horizontais com seleção explícita, data, motivo, estado e ações clínicas existentes. Filtros SHALL preceder paginação e distinguir falha, carregamento e vazio. SHALL preservar o menu médico restrito e o assistente flutuante. O campo de busca SHALL ter contorno arredondado pill, e o filtro SHALL apresentar um ícone de ajustes. A aba Canceladas SHALL listar somente status cancelada, excluído das abas ativas, e seus cards SHALL NOT oferecer iniciar/retomar. Não será criada uma operação de cancelamento.

#### Scenario: Buscar e paginar
- **WHEN** o médico altera aba, busca ou estado
- **THEN** a lista inicia na página 1 e o total corresponde ao filtro aplicado no backend

#### Scenario: Consultas canceladas
- **WHEN** o médico seleciona Canceladas
- **THEN** recebe somente registros cancelados, respeitando paginação e autorização, sem ação de iniciar atendimento

#### Scenario: Contrato anterior
- **WHEN** o backend ainda não confirma o contrato de filtros
- **THEN** a tela informa a indisponibilidade sem apresentar dados como filtrados

### Requirement: Resumo autorizado do paciente selecionado
O sistema SHALL apresentar o resumo do pet escolhido com foto disponível, nome, peso informado, última vacina, última consulta e alergias explicitamente identificadas nos registros de doenças/diagnósticos, incluindo estado e indicação da fonte. Ausência SHALL ser apresentada como informação não registrada, sem afirmar ausência clínica de alergias. SHALL incluir babyturtle.png decorativa sem interceptar ações.

#### Scenario: Seleção com consentimento
- **GIVEN** o veterinário tem autorização ativa para o pet
- **WHEN** seleciona seu card
- **THEN** o backend valida o acesso e audita a leitura, e a página mostra apenas o resumo correspondente à seleção atual

#### Scenario: Revogação ou resposta antiga
- **GIVEN** o consentimento foi revogado ou o médico mudou de seleção/sessão
- **WHEN** a leitura falha ou chega uma resposta antiga
- **THEN** dados anteriores são limpos e a resposta não ocupa o resumo de outro paciente

#### Scenario: Sem registro de alergia
- **WHEN** o histórico não contém doença ou diagnóstico identificado como alergia
- **THEN** o resumo mostra “Alergias não informadas” e não usa peso como alergia

### Requirement: LED de estado nos cards de Consultas
O sistema SHALL apresentar um segmento luminoso contornando o card no sentido horário: verde para consultas finalizadas, vermelho para agendadas ainda não iniciadas e amarelo para em atendimento. O halo da mesma cor SHALL acompanhar somente o segmento móvel, sem transformar toda a caixa em brilho estático. SHALL preservar os estados textuais, cliques, seleção, responsividade, temas, menu e assistente. Canceladas e estados desconhecidos SHALL permanecer sem LED. Movimento reduzido SHALL desacelerar a circulação.

#### Scenario: Cor e movimento por estado
- **WHEN** um card de consulta é exibido
- **THEN** o LED assume a cor correspondente ao status real e percorre continuamente o perímetro com sombra móvel da mesma cor

#### Scenario: Interação e adaptação
- **WHEN** o médico seleciona o pet, abre o prontuário ou usa a página em celular, tema escuro ou movimento reduzido
- **THEN** controles continuam acessíveis, o contorno acompanha o tamanho do card e a animação permanece horária, mais lenta com movimento reduzido

### Requirement: LED contextual no resumo do paciente
O resumo do paciente SHALL reutilizar o LED horário e halo móvel dos cards, com vermelho/agendada, amarelo/em atendimento e verde/finalizada, conforme a consulta selecionada e carregada com autorização. SHALL acompanhar trocas de seleção sem reaproveitar o estado de outro card. Sem seleção, em erro/carregamento, canceladas ou estado desconhecido, SHALL permanecer sem LED.

#### Scenario: Alternar consulta selecionada
- **WHEN** o médico seleciona consultas com estados diferentes
- **THEN** o resumo confirmado assume a cor da consulta atual e mantém a mesma circulação horária e sombra móvel

#### Scenario: Limpar ou falhar seleção
- **WHEN** a seleção é limpa, está carregando ou a leitura autorizada falha
- **THEN** o resumo não mantém o LED da consulta anterior

### Requirement: Paleta do atendimento em todos os elementos contextuais
Cards de consultas e resumo confirmado SHALL aplicar a paleta do status (vermelho/agendada, amarelo/em atendimento, verde/finalizada) aos botões, ícones, badge, nome, bordas, foco, avatar sem foto e superfícies suaves. SHALL manter contraste nos temas claro/escuro, usando tons escuros para texto sobre fundos claros e texto escuro no botão amarelo. Foto real e mascote SHALL preservar suas cores. Estados neutros e cancelados SHALL ter apresentação neutra. Menus e assistente SHALL ser preservados.

#### Scenario: Troca da paleta contextual
- **WHEN** o médico seleciona consulta em outro estado ou muda de tema
- **THEN** o resumo e seus elementos adotam a paleta da seleção atual sem resíduos verdes nos estados vermelho/amarelo, mantendo legibilidade e LED em movimento

#### Scenario: Imagem do paciente
- **WHEN** não há foto cadastrada ou uma foto existente falha ao carregar
- **THEN** a patinha vetorial aparece somente para foto nula/vazia e acompanha a paleta do status; foto existente com erro indica falha sem patinha, e foto carregada aparece sem patinha sobreposta

#### Scenario: Mesmo tom no resumo e na seleção
- **WHEN** um resumo autorizado está exibido para o card selecionado
- **THEN** fundo e borda usam exatamente os mesmos tons do card selecionado, inclusive no tema claro e escuro

### Requirement: Cards de Horários com paleta do atendimento
Cards de Horários SHALL compartilhar a paleta de Consultas: vermelho/agendada, amarelo/em atendimento, verde/finalizada, incluindo nome, ícones, badge, botões, fundo, bordas e foco. O LED circular da foto SHALL usar a cor e halo do status, mantendo movimento horário e desaceleração com movimento reduzido. Ações, autorização e dados da agenda SHALL ser preservados.

#### Scenario: Horários com estados diferentes
- **WHEN** a agenda mostra consultas agendadas, em atendimento e concluídas
- **THEN** seus cards usam vermelho, amarelo e verde respectivamente em ambos os temas, com controles legíveis e funcionais

### Requirement: Atendimento segue a situação clínica
O formulário Atendimento SHALL usar a paleta do status confirmado (vermelho/agendada, amarelo/em atendimento, verde/finalizada) em ações, ícones, destaques, bordas e superfícies, inclusive nos painéis de histórico e calendário abertos nessa página. SHALL preservar contraste, vidro, wallpaper, preferências de tema, dados, rascunho e eventos.

#### Scenario: Formulário em atendimento
- **WHEN** uma consulta em atendimento é aberta nos temas claro ou escuro
- **THEN** formulário e painéis adotam amarelo com texto legível e preservam edição, histórico e calendário

### Requirement: LED no painel completo do atendimento
O painel inteiro do formulário SHALL apresentar segmento luminoso no perímetro com cor do status e halo móvel da mesma cor, girando continuamente no sentido horário. SHALL acompanhar altura dinâmica, não interceptar cliques e desacelerar com movimento reduzido. Sem status reconhecido SHALL permanecer sem LED.

#### Scenario: Alterar conteúdo do formulário
- **WHEN** o médico adiciona registros, redimensiona a tela ou solicita movimento reduzido
- **THEN** o LED acompanha o perímetro completo e mantém circulação horária, mais lenta em movimento reduzido

### Requirement: Card de identidade profissional na sidebar médica
O sistema SHALL apresentar nome, avatar de iniciais, indicação de perfil médico, CRMV/UF reais da própria conta e logout em card consistente com o design existente, nos temas claro/escuro e drawer móvel. A sidebar compacta SHALL preservar avatar e saída acessível sem overflow. Destinos e proteção de saída em Configurações SHALL permanecer iguais. SHALL NOT declarar verificação externa do registro.

#### Scenario: Carregar registro profissional
- **GIVEN** sessão veterinária válida
- **WHEN** o card é montado
- **THEN** obtém CRMV/UF pela leitura autenticada da própria conta, sem bloquear navegação, e reutiliza metadados confirmados da sessão

#### Scenario: Troca de sessão ou perfil
- **GIVEN** uma leitura está em andamento
- **WHEN** a sessão, identidade, token ou perfil muda
- **THEN** a resposta antiga não restaura metadados e os dados profissionais são limpos ao sair

#### Scenario: Ausência ou falha
- **WHEN** o registro não está preenchido ou a leitura falha
- **THEN** apresenta informação honesta e permite repetir em caso de falha, sem inventar CRMV/UF
