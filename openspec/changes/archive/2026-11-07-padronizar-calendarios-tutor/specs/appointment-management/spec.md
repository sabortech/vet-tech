# Spec Delta

## ADDED Requirements

### Requirement: Agendamento do tutor usa o painel compartilhado de calendário
O agendamento do tutor SHALL usar o painel visual já presente na área médica, com seletores de mês e ano, navegação mensal, indicação de hoje e data selecionada, LED de contorno e apresentação responsiva nos dois temas. A primeira etapa SHALL integrar escolha do dia e horário, manter o pet de contexto e permitir avançar para motivo e profissional. Datas anteriores ao dia atual em America/Sao_Paulo SHALL ficar indisponíveis. Escolher mês ou ano SHALL NOT alterar silenciosamente o dia selecionado. A escolha de dia não SHALL fechar o agendamento. A data selecionada SHALL ser apresentada também em campo próprio abaixo do calendário, em formato brasileiro e somente leitura, separado do campo de horário.

#### Scenario: Escolher dia e horário
- **WHEN** o tutor abre Agendar consulta, navega no mês/ano e escolhe um dia permitido
- **THEN** a data é destacada e apresentada em formato brasileiro, mantendo horário de 08h–17h e a etapa seguinte do fluxo existente

#### Scenario: Data passada ou operação protegida
- **WHEN** o tutor tenta selecionar um dia passado ou alterar uma reserva durante envio ou confirmação de resultado incerto
- **THEN** a seleção é impedida também pelo evento do servidor, preservando o envio existente

#### Scenario: Cancelar e voltar
- **WHEN** o tutor cancela a primeira etapa ou volta da segunda
- **THEN** a operação conserva as regras existentes de cancelamento e a data válida escolhida não é trocada pela navegação do calendário
