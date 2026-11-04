## MODIFIED Requirements

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

## ADDED Requirements

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
