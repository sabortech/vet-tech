# Spec Delta

## ADDED Requirements

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
- **WHEN** não há foto ou a imagem falha ao carregar
- **THEN** a patinha vetorial acompanha a paleta do status; com foto carregada, a foto original aparece sem patinha sobreposta

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
