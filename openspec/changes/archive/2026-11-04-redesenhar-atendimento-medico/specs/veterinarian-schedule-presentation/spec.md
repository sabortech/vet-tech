## ADDED Requirements

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
O sistema SHALL usar acabamento verde nos cards de Horários e Consultas, preservando dados, estados textuais e ações autorizadas. SHALL apresentar LED verde percorrendo no sentido horário somente o perímetro da agenda do dia e da moldura da foto/fallback do pet, além do calendário existente. O trecho iluminado SHALL projetar halo da mesma cor que acompanha somente o segmento móvel, inclusive no calendário e chat, sem iluminar estaticamente toda a borda. O conteúdo SHALL permanecer imóvel, legível e clicável; movimento reduzido SHALL desacelerar a circulação.

#### Scenario: Card em atendimento ou concluído
- **WHEN** a agenda apresenta consultas em atendimento ou finalizadas
- **THEN** o card usa detalhes verdes com estado textual correspondente e a foto/fallback possui contorno luminoso em circulação

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
