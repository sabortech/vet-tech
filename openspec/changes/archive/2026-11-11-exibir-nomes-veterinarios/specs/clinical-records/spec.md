## ADDED Requirements

### Requirement: Identificação nominal do veterinário
O sistema SHALL apresentar o nome do veterinário em todos os campos do profissional nos registros clínicos, autorizações e PDF, mantendo identificadores apenas para operações internas. Sem nome disponível, SHALL exibir “Nome não informado”.

#### Scenario: Registro autorizado com profissional
- **GIVEN** usuário autorizado a consultar o registro
- **WHEN** consulta seus campos ou exporta PDF
- **THEN** o profissional aparece pelo nome, preservando autorização e auditoria existentes

#### Scenario: Nome ausente
- **WHEN** o vínculo profissional não possui nome disponível
- **THEN** a interface exibe “Nome não informado” sem substituir pelo ID
