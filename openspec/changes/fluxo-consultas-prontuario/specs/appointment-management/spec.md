## Purpose

Permitir ao tutor marcar atendimento para um pet próprio e ao veterinário acompanhar sua agenda por data, iniciando o atendimento na plataforma.

## ADDED Requirements

### Requirement: Tutor agenda para pet próprio com profissional compatível
O sistema SHALL permitir ao tutor autenticado escolher um pet próprio, um veterinário que atenda sua espécie, data, horário e motivo. A confirmação SHALL registrar a consulta como agendada e conceder o acesso prévio informado ao profissional escolhido. A identidade do tutor SHALL ser derivada da sessão.

#### Scenario: Agendamento confirmado
- **GIVEN** um tutor possui o pet e seleciona profissional compatível
- **WHEN** confirma os dados com a informação de liberação do prontuário visível
- **THEN** recebe a consulta agendada com data e profissional e o consentimento é registrado na mesma operação

#### Scenario: Pet alheio ou profissional incompatível
- **GIVEN** o pedido contém pet alheio ou profissional que não atende sua espécie
- **WHEN** o backend valida o agendamento
- **THEN** rejeita o pedido sem criar consulta nem autorização

### Requirement: Escolha livre respeita horário comercial
O sistema SHALL aceitar início de consulta entre 08h e 17h inclusive, com precisão de minutos, no fuso America/Sao_Paulo. SHALL rejeitar agendamento no passado ou fora dessa faixa. A escolha SHALL ser livre, sem grade prévia do veterinário, duração obrigatória ou aprovação posterior neste MVP.

#### Scenario: Limites do expediente
- **WHEN** o tutor agenda em data futura às 08h ou às 17h
- **THEN** o horário é aceito se não houver conflito

#### Scenario: Horário inválido
- **WHEN** o tutor envia data/hora passada, 07h59 ou 17h01 no fuso do serviço
- **THEN** o backend rejeita e informa o campo a corrigir

### Requirement: Um mesmo início não gera reservas conflitantes
O sistema SHALL impedir duas consultas no mesmo instante de início para o mesmo veterinário ou para o mesmo pet, inclusive sob concorrência. Uma repetição do mesmo pedido SHALL retornar a reserva original sem duplicar consulta ou autorização. Não SHALL inferir intervalos de sobreposição sem duração definida.

#### Scenario: Concorrência de horário
- **WHEN** dois pedidos distintos disputam o mesmo profissional e instante de início
- **THEN** somente um confirma e o outro recebe conflito sem dados do tutor concorrente

#### Scenario: Reenvio após perda da resposta
- **WHEN** o tutor reenvia o mesmo pedido com a mesma identificação de operação
- **THEN** recebe o resultado original e há somente uma consulta

### Requirement: Horários apresenta calendário vertical do profissional
O sistema SHALL oferecer Horários no menu lateral veterinário, abrindo uma tela com calendário vertical por horário e consultas próprias do dia selecionado. SHALL iniciar no dia atual, permitir trocar a data e apresentar horário, pet quando autorizado e estado. A grade visual SHALL NOT impor duração ou horários pré-disponibilizados ao tutor.

#### Scenario: Escolher outro dia
- **WHEN** o veterinário abre Horários e seleciona uma data
- **THEN** a tela posiciona suas consultas no calendário vertical por horário ou apresenta estado vazio

#### Scenario: Isolamento da agenda
- **GIVEN** existem consultas de dois veterinários
- **WHEN** um deles consulta ou manipula identificadores da agenda
- **THEN** o backend não revela consultas do outro profissional

### Requirement: Consultas reúne próximos atendimentos e suas ações
O sistema SHALL oferecer Consultas no menu lateral veterinário, abrindo lista própria ordenada por data/hora, com próximos agendamentos e acesso aos atendimentos ainda em aberto. Começar consulta e Retomar SHALL ficar nessa lista, levando à tela clínica. Consultas finalizadas SHALL NOT continuar como pendências.

#### Scenario: Próximas consultas em dias diferentes
- **WHEN** o veterinário abre Consultas
- **THEN** vê os próximos atendimentos de diferentes dias em ordem cronológica, independentemente do dia selecionado em Horários

#### Scenario: Atendimento pendente após o horário previsto
- **WHEN** um agendamento ultrapassa seu horário ou um atendimento iniciado permanece aberto
- **THEN** continua acessível como pendência na lista, com Começar consulta ou Retomar conforme seu estado

#### Scenario: Abrir a tela de atendimento
- **GIVEN** há autorização ativa para uma consulta atribuída ao profissional
- **WHEN** ele aciona Começar consulta na lista Consultas
- **THEN** o backend inicia o atendimento e a interface abre a tela própria do prontuário

### Requirement: Início do atendimento é manual
O sistema SHALL oferecer Começar consulta para consulta agendada do veterinário responsável com consentimento ativo. A operação SHALL registrar o início real, mudar o estado para em atendimento e abrir a tela própria do prontuário. Não SHALL condicionar o início ao relógio ter atingido a data/hora agendada.

#### Scenario: Começar antes do horário previsto
- **GIVEN** a consulta está agendada para o profissional e há consentimento ativo
- **WHEN** ele aciona Começar consulta antes do horário previsto
- **THEN** a consulta entra em atendimento e a tela do prontuário é aberta

#### Scenario: Retomar atendimento
- **WHEN** o profissional volta a uma consulta já em atendimento
- **THEN** retoma o rascunho salvo sem criar outra consulta nem substituir o início registrado
