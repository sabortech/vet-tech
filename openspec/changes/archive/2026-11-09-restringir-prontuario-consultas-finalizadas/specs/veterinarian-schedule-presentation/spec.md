# Spec Delta

## MODIFIED Requirements

### Requirement: Histórico dos cards usa o painel compartilhado
O sistema SHALL abrir o mesmo painel de histórico do atendimento a partir dos cards autorizados em Horários e Consultas, usando o pet daquele card. Na aba Consultas, a ação Ver Histórico anterior SHALL aparecer somente em cards com status explícito `finalizada`; consultas agendadas, em atendimento, canceladas ou de estado desconhecido SHALL NOT exibir essa ação. Os botões Exportar PDF e Ver Histórico anterior SHALL ter a mesma largura e altura; o rótulo Ver Histórico anterior SHALL permanecer em uma linha. SHALL incluir carregamento, falha/nova tentativa, vazio, categorias clínicas, tema e mascote. Nova tentativa SHALL manter o mesmo alvo. Fechamento SHALL restaurar foco ao acionador. O histórico SHALL NOT aparecer inline abaixo da agenda nem modificar o atendimento aberto.

#### Scenario: Abrir histórico de outro pet
- **GIVEN** o veterinário possui autorização vigente para o pet do card
- **WHEN** abre seu histórico após ter atendido outro pet, ou repete uma leitura que falhou
- **THEN** o painel solicita o pet do card pelas mesmas APIs autorizadas e auditadas e preserva o rascunho de atendimento

#### Scenario: Botão depende da finalização na aba Consultas
- **WHEN** o médico visualiza cards autorizados em diferentes estados na aba Consultas
- **THEN** Ver Histórico anterior aparece somente nas finalizadas, e iniciar/retomar continuam disponíveis nos estados correspondentes

#### Scenario: Consulta finalizada sem autorização
- **GIVEN** a autorização do tutor foi revogada
- **WHEN** o card finalizado é apresentado
- **THEN** Ver Histórico anterior permanece indisponível, preservando a proteção existente no backend
