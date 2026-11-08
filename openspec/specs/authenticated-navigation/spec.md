# authenticated-navigation Specification

## Purpose

Organizar a área autenticada do tutor com navegação consistente por pet e acesso ao cadastro e alternância existentes, preparando os próximos módulos clínicos.

## Requirements

### Requirement: Menu retrátil preserva o contexto
O sistema SHALL usar o mesmo menu personalizado das outras telas do tutor e exibir Dashboard, Prontuário, Vacinas, Medicamentos, Doenças e Consultas nessa ordem, seguidos de Exames (indisponível), Meus Pets, Mudar pet e Configurações, com somente Sair no rodapé e sem entrada Novo pet. Prontuário SHALL representar Início. O Dashboard SHALL ser um destino distinto do Prontuário. O menu SHALL manter cantos arredondados e fundo contínuo ao redor das bordas em todas as telas, inclusive Dashboard. A marca SHALL usar a tartaruga em V ao lado do nome Vet Tech e o controle de abrir/recolher SHALL usar três barras. O menu SHALL recolher e expandir sem alterar o pet ativo; o escopo selecionado no Dashboard SHALL NOT alterar essa seleção clínica. A seção ativa e o pet atual SHALL ser identificáveis, com nomes acessíveis e operação por teclado em desktop e celular.

#### Scenario: Recolher menu
- **WHEN** o tutor recolhe e expande o menu com um pet aberto
- **THEN** o pet continua selecionado e os controles permanecem identificáveis e utilizáveis

#### Scenario: Celular
- **WHEN** o tutor navega em uma tela estreita
- **THEN** consegue alcançar menu, conteúdo e ações inferiores sem corte ou rolagem horizontal

#### Scenario: Preservar o pet entre áreas
- **GIVEN** o tutor abriu um pet autorizado
- **WHEN** visita Configurações ou Meus Pets e retorna a uma seção clínica pelo menu
- **THEN** a seção usa a mesma seleção e a preferência de expansão permanece consistente
- **AND** a navegação não limpa o pet nem dispara atualização clínica apenas por renderizar o menu

#### Scenario: Loading não bloqueia o menu compartilhado
- **WHEN** o tutor troca de seção enquanto uma leitura clínica está pendente
- **THEN** a navegação permanece disponível, o loading continua identificável e a leitura pendente não é duplicada

#### Scenario: Alterar escopo no Dashboard
- **GIVEN** o tutor possui um pet selecionado no prontuário
- **WHEN** altera o filtro do Dashboard entre “Todos os pets” e um pet específico
- **THEN** a seleção do prontuário não é alterada e o escopo do Dashboard é identificável

### Requirement: Início e seções seguem o pet autorizado
O sistema SHALL manter os dados básicos do pet validado em Início e usar a mesma seleção em Consultas, Vacinas, Medicamentos e Doenças. Consultas SHALL reunir agendamentos e prontuários estruturados finalizados, sem exigir documento. Sem pet selecionado SHALL orientar escolha/cadastro; sem registros SHALL mostrar estado vazio, sem dados fictícios. A navegação SHALL preservar o isolamento de sessão e contexto.

#### Scenario: Nova sessão sem seleção
- **WHEN** o tutor entra mesmo possuindo um único pet
- **THEN** recebe orientação de escolha explícita sem seleção automática

#### Scenario: Troca de animal
- **WHEN** o tutor muda de pet
- **THEN** os dados anteriores deixam de aparecer e somente a resposta da seleção atual pode preencher Início ou outra seção

#### Scenario: Abrir consulta concluída
- **WHEN** o tutor escolhe uma consulta finalizada do pet selecionado
- **THEN** lê data, profissional, diagnóstico, observações e complementos publicados no conteúdo principal, mantendo o pet identificado

#### Scenario: Seções consolidadas
- **WHEN** o tutor escolhe Vacinas, Medicamentos ou Doenças
- **THEN** vê somente registros publicados do pet atual, com datas e acesso à consulta de origem quando existente

### Requirement: Mudar pet reutiliza seleção segura
O sistema SHALL encaminhar Mudar pet para um modo de seleção de Meus Pets com somente a lista dos pets próprios, sem formulário de cadastro, e permitir nova escolha. A mesma tartaruga espreitando do seletor de datas SHALL aparecer decorativamente à esquerda da lista, nos dois temas e celular. As validações de propriedade, limpeza de contexto e descarte de respostas atrasadas SHALL permanecer. A entrada normal Meus Pets SHALL continuar mostrando cadastro e lista, e Logout SHALL permanecer acessível.

#### Scenario: Escolher outro pet
- **GIVEN** o tutor possui A aberto e também é dono de B
- **WHEN** aciona Mudar pet e escolhe B
- **THEN** os dados de A são limpos e B só é exibido após autorização do backend

#### Scenario: Seleção isolada e retorno
- **WHEN** o tutor aciona Mudar pet
- **THEN** abre somente a lista com a tartaruga à esquerda, podendo escolher um pet ou voltar à tela completa de Meus Pets

### Requirement: Dashboard do tutor abre agendamento em duas etapas
O sistema SHALL oferecer Agendar consulta na tela inicial do tutor, abrindo pop-up com duas etapas: dia/horário e pet/motivo/profissional compatível. A abertura SHALL dispensar pet previamente selecionado no dashboard. A informação de liberação prévia ao veterinário SHALL aparecer antes da confirmação. A seleção no pop-up SHALL NOT trocar silenciosamente o pet aberto no dashboard.

#### Scenario: Abrir a partir da tela inicial
- **WHEN** o tutor aciona Agendar consulta no dashboard, mesmo sem pet aberto
- **THEN** o pop-up abre na etapa de calendário para escolher dia e horário

#### Scenario: Segunda etapa e confirmação
- **WHEN** o tutor avança com dia/horário válidos
- **THEN** seleciona um pet próprio, informa o motivo e escolhe veterinário compatível antes de confirmar a reserva e a liberação de acesso

### Requirement: Pop-up permite voltar e fechar sem reserva parcial
O sistema SHALL preservar os campos ao voltar entre etapas e somente gravar consulta/autorização na confirmação final. Fechar antes de enviar SHALL descartar o rascunho local e devolver foco ao botão. Trocar o pet no pop-up SHALL invalidar profissional incompatível e respostas da seleção anterior. Sessão encerrada SHALL limpar o formulário.

#### Scenario: Voltar para corrigir a data
- **WHEN** o tutor volta da segunda para a primeira etapa e altera dia/horário
- **THEN** os demais campos continuam preenchidos e a confirmação usa a data/hora atualizada, sem criar reserva intermediária

#### Scenario: Fechar antes de confirmar
- **WHEN** o tutor fecha o pop-up sem enviar
- **THEN** nenhuma consulta ou autorização é criada e o foco retorna ao botão de abertura

#### Scenario: Tutor sem pets
- **WHEN** o tutor sem pets chega à segunda etapa
- **THEN** recebe orientação para cadastrar um pet, sem opção inventada nem envio de reserva

### Requirement: Consultas do tutor mantém histórico e acessos do pet
O sistema SHALL oferecer lista de agendamentos, histórico finalizado, permissões e auditoria em Consultas do tutor para o pet selecionado. Essa seção SHALL usar a mesma fonte dos agendamentos criados pelo pop-up. Horários e Consultas do profissional SHALL permanecer na área veterinária.

#### Scenario: Conferir reserva criada no dashboard
- **WHEN** o tutor abre Consultas do pet escolhido no agendamento
- **THEN** vê a reserva confirmada com data, profissional e estado

#### Scenario: Consultas de outro pet
- **WHEN** o tutor alterna o animal durante uma leitura da seção Consultas
- **THEN** resultados da seleção anterior são descartados e não aparecem como pertencentes ao novo pet

### Requirement: Ações clínicas compartilham a aparência do menu
O sistema SHALL apresentar Mudar pet e Sair no contexto clínico usando os mesmos padrões de ícone, espaçamento, foco, tema e identificação acessível dos demais itens. Mudar pet e Sair SHALL preservar suas regras existentes de limpeza e descarte de respostas antigas.

#### Scenario: Voltar à escolha durante carregamento
- **WHEN** o tutor aciona Mudar pet enquanto aguarda uma leitura
- **THEN** retorna à escolha e a resposta antiga não reabre nem preenche o animal anterior

#### Scenario: Sair durante carregamento
- **WHEN** o tutor encerra a sessão com uma leitura clínica pendente
- **THEN** a sessão e o contexto são limpos e a resposta pendente não repõe dados no menu ou no conteúdo

### Requirement: Menu do tutor mantém entradas e saída em posições consistentes
Todas as telas autenticadas do tutor SHALL mostrar Mudar pet junto às entradas principais da sidebar, seguido imediatamente de Configurações, e somente Sair no rodapé. Novo pet SHALL NOT aparecer como entrada do menu; cadastro SHALL permanecer em Meus Pets. Em telas baixas a lista de navegação SHALL poder rolar, preservando a saída acessível. Configurações SHALL manter confirmação de descarte antes de Mudar pet ou Sair com dados não salvos. O menu veterinário SHALL preservar suas entradas próprias.

#### Scenario: Navegar entre abas
- **WHEN** o tutor abre Meus Pets, Dashboard, seções clínicas ou Configurações
- **THEN** encontra as mesmas entradas na mesma ordem e Sair no rodapé

### Requirement: Seções sem pet usam orientação comum
Prontuário, Vacinas, Medicamentos, Doenças e Consultas SHALL apresentar a mesma tela ilustrada sem pet alvo selecionado, com botão para selecionar pet em Meus Pets. A arte SHALL ter versões clara e escura alternadas pelo tema, preservando a cena e a legibilidade do título e botão em desktop e celular. A lista de escolha SHALL aparecer somente em Meus Pets. Dashboard global e Configurações SHALL continuar acessíveis sem seleção. Seleção em Meus Pets SHALL abrir o Dashboard com o pet escolhido no filtro; durante leitura SHALL mostrar carregamento e, em falha, permitir nova tentativa sem expor dados de outro pet.

#### Scenario: Navegar sem seleção
- **WHEN** o tutor visita qualquer seção clínica sem pet alvo
- **THEN** vê a mesma arte e botão para Meus Pets, sem lista repetida ou ações clínicas sem contexto

#### Scenario: Selecionar e trocar
- **WHEN** o tutor escolhe um pet próprio em Meus Pets
- **THEN** abre o Dashboard com o filtro desse pet e mantém a seleção nas seções clínicas
- **AND** Mudar pet ou Voltar à lista limpam o contexto e abrem Meus Pets, descartando respostas antigas

### Requirement: Arte ocupa a área principal inteira
Sem pet alvo, a arte SHALL preencher toda a área de conteúdo ao lado da sidebar, sem moldura ou margens de painel, nos dois temas. O botão e orientação SHALL permanecer legíveis e acessíveis em telas estreitas.

#### Scenario: Abrir seção sem seleção
- **WHEN** o tutor acessa uma seção clínica sem pet alvo
- **THEN** o wallpaper cobre a área principal inteira e a orientação aparece sobre ele

### Requirement: Contorno verde animado na cena
A cena central SHALL ter um segmento LED verde percorrendo seu contorno em sentido horário nos dois temas, sem bloquear interações. A posição SHALL acompanhar a arte no desktop e celular; movimento reduzido SHALL tornar o ciclo mais lento.

#### Scenario: Visualizar cena sem seleção
- **WHEN** o tutor visualiza a orientação sem pet
- **THEN** o LED verde percorre o contorno da cena em sentido horário e o botão continua acessível

### Requirement: Lista alinha ações e identifica seleção no botão
Meus Pets SHALL alinhar botões em uma coluna de largura uniforme e acomodar textos longos sem sobreposição. O botão do pet autorizado selecionado SHALL mostrar “Pet selecionado”, ícone e cor distinta; SHALL NOT duplicar esse aviso ao lado. Carregamento SHALL ser explícito sem indicar seleção antes de sucesso.

#### Scenario: Lista com metadados de tamanhos diferentes
- **WHEN** o tutor visualiza seus pets
- **THEN** os botões ficam alinhados e o botão do pet selecionado usa texto e destaque de seleção

### Requirement: Abrir pet direciona ao Dashboard individual
Ao abrir um pet em Meus Pets, o sistema SHALL abrir o Dashboard com o filtro correspondente ao pet escolhido e manter sua seleção clínica autorizada. Trocar o pet SHALL substituir o escopo anterior sem aceitar respostas antigas como pertencentes ao novo contexto.

#### Scenario: Abrir outro pet da lista
- **WHEN** o tutor abre um pet próprio em Meus Pets
- **THEN** acessa o Dashboard com esse pet no filtro, inclusive se havia outro escopo selecionado

### Requirement: Prontuário destaca identidade e dados do pet
O Prontuário SHALL apresentar foto circular com borda fina e neutra, nome, espécie, raça e mascote, seguidos de cartões para sexo, nascimento, peso atual, pelagem e microchip. SHALL preservar ausência explícita, valores zero e dados autorizados, sem inventar unidades. SHALL adaptar-se ao celular e tema escuro mantendo voltar, agendar, atualizar e nova tentativa acessíveis.

#### Scenario: Pet com dados completos ou ausentes
- **WHEN** o tutor abre o Prontuário do pet selecionado
- **THEN** vê identidade destacada e cinco cartões, com imagem substituta sem foto e indicação de ausência nos campos vazios

### Requirement: LED verde nas molduras do Prontuário
O Prontuário SHALL apresentar LED verde percorrendo no sentido horário o contorno da foto, do cartão de identificação e de todos os cartões de dados, nos dois temas. A decoração SHALL acompanhar a forma da moldura e o layout responsivo, sem bloquear ações nem gerar consultas remotas; movimento reduzido SHALL usar ciclo mais lento.

#### Scenario: Visualizar Prontuário do pet
- **WHEN** os dados autorizados do pet aparecem no Prontuário
- **THEN** foto, identificação e cinco cartões exibem seus LEDs verdes acompanhando os respectivos contornos

### Requirement: Aba Vacinas organiza registros com clareza
A aba Vacinas SHALL manter cabeçalho e lista de registros, com nome da vacina destacado, aplicação, lote e próxima dose organizados, e origem/veterinário junto de ação para consulta de origem quando disponível. SHALL manter estados vazios, carregamento e erro e adaptação aos dois temas e celular. SHALL NOT acrescentar banner de pet ou mascote nessa aba.

#### Scenario: Ler vacina e abrir origem
- **WHEN** o tutor visualiza uma vacina publicada
- **THEN** os dados e a origem aparecem organizados e o botão abre a consulta correspondente sem alterar o pet selecionado

### Requirement: Medicamentos apresenta prescrição em cartão organizado
A aba Medicamentos SHALL apresentar nome destacado, dose, frequência, via, tipo, início, fim, consulta e veterinário quando registrados, com ausência explícita e botão da consulta de origem. SHALL usar símbolo de medicamento em disco translúcido sobre o cenário lateral, adaptar temas e celular e preservar estados de carregamento/erro/vazio. SHALL NOT inferir status ativo ou tratamento concluído a partir dos registros.

#### Scenario: Conferir medicamento publicado
- **WHEN** o tutor acessa Medicamentos do pet selecionado
- **THEN** vê campos organizados em grupos e consegue abrir a consulta de origem correta sem perder o contexto do pet

### Requirement: Fundos variados por registro clínico
Cada cartão de Vacinas e Medicamentos SHALL receber um fundo sorteado entre os cenários locais disponíveis. Novos registros SHALL priorizar fundos ainda não usados na lista até esgotar opções. A escolha SHALL permanecer estável durante atualizações e navegação na mesma sessão, com isolamento por pet e tipo de registro. O símbolo da respectiva aba SHALL permanecer estável sobre o fundo sorteado, com transparência discreta.

#### Scenario: Adicionar registro e atualizar a lista
- **WHEN** outro registro aparece na lista clínica autorizada
- **THEN** seu cartão recebe um fundo do catálogo sem trocar os fundos já atribuídos aos registros existentes

### Requirement: Dashboard geral identifica pet selecionado em Meus Pets
Na visão Todos os pets, o Dashboard SHALL mostrar um botão dentro do card do pet selecionado em Meus Pets, no cabeçalho entre seu nome e a mascote em V. Acionar o botão SHALL selecionar esse pet no filtro do Dashboard. Sem seleção, nos outros cards e na visão individual SHALL ocultar o botão. O controle SHALL adaptar-se aos temas e celular sem sobrepor nome ou mascote.

#### Scenario: Conferir contexto na visão geral
- **WHEN** o tutor abre Todos os pets com um pet selecionado em Meus Pets
- **THEN** o botão no cabeçalho do card selecionado identifica esse pet e permite abrir sua visão individual
