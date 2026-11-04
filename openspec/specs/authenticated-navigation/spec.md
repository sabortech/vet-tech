# authenticated-navigation Specification

## Purpose

Organizar a área autenticada do tutor com navegação consistente por pet e acesso ao cadastro e alternância existentes, preparando os próximos módulos clínicos.

## Requirements

### Requirement: Menu retrátil preserva o contexto
O sistema SHALL usar o mesmo menu personalizado das outras telas do tutor e exibir Dashboard, Prontuário, Vacinas, Medicamentos, Doenças e Consultas nessa ordem, com Novo pet e Mudar pet na parte inferior do contexto clínico. Prontuário SHALL representar Início. O Dashboard SHALL ser um destino distinto do Prontuário. O menu SHALL recolher e expandir sem alterar o pet ativo; o escopo selecionado no Dashboard SHALL NOT alterar essa seleção clínica. A seção ativa e o pet atual SHALL ser identificáveis, com nomes acessíveis e operação por teclado em desktop e celular.

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

### Requirement: Novo pet abre cadastro em modal
O sistema SHALL abrir o cadastro existente em modal por Novo pet, removendo-o da apresentação permanente de Início. O modal SHALL permitir teclado, foco inicial, fechamento e retorno de foco; cancelar SHALL NOT criar pet. Sucesso SHALL atualizar a lista sem trocar silenciosamente o pet ativo; falhas SHALL manter correção e nova tentativa disponíveis. Abrir ou fechar o modal SHALL preservar a rota clínica atual.

#### Scenario: Cancelar cadastro
- **WHEN** o tutor fecha o modal sem submeter
- **THEN** nenhum registro é criado e o foco volta ao controle de abertura

#### Scenario: Cadastro válido
- **WHEN** a API confirma o novo pet
- **THEN** a lista é atualizada e o pet previamente selecionado permanece o mesmo, sujeito à revalidação existente

#### Scenario: Modal não redireciona ao login
- **GIVEN** o tutor está em uma seção do Prontuário
- **WHEN** abre Novo pet e depois cancela o modal
- **THEN** continua na mesma rota e seção, sem ser redirecionado para `/login`

### Requirement: Mudar pet reutiliza seleção segura
O sistema SHALL oferecer a lista dos pets próprios por Mudar pet e permitir nova escolha, mantendo as validações de propriedade, limpeza de contexto e descarte de respostas atrasadas existentes. Logout SHALL permanecer acessível.

#### Scenario: Escolher outro pet
- **GIVEN** o tutor possui A aberto e também é dono de B
- **WHEN** aciona Mudar pet e escolhe B
- **THEN** os dados de A são limpos e B só é exibido após autorização do backend

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
O sistema SHALL apresentar Novo pet, Mudar pet e Sair no contexto clínico usando os mesmos padrões de ícone, espaçamento, foco, tema e identificação acessível dos demais itens. Mudar pet e Sair SHALL preservar suas regras existentes de limpeza e descarte de respostas antigas.

#### Scenario: Voltar à escolha durante carregamento
- **WHEN** o tutor aciona Mudar pet enquanto aguarda uma leitura
- **THEN** retorna à escolha e a resposta antiga não reabre nem preenche o animal anterior

#### Scenario: Sair durante carregamento
- **WHEN** o tutor encerra a sessão com uma leitura clínica pendente
- **THEN** a sessão e o contexto são limpos e a resposta pendente não repõe dados no menu ou no conteúdo
