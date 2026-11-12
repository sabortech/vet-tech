## ADDED Requirements

### Requirement: Peso cadastrado apresentado em quilogramas
O sistema SHALL apresentar o peso cadastrado com a unidade Kg, mantendo o valor registrado e usando “Não informado” quando ausente. Zero SHALL ser exibido como “0 Kg”. A convenção Kg SHALL ser explícita no cadastro e nas exibições do Dashboard e Prontuário; não haverá conversão ou alteração de valores armazenados.

#### Scenario: Peso disponível
- **WHEN** o pet possui peso cadastrado 5
- **THEN** o campo de peso exibe “5 Kg”

#### Scenario: Peso ausente
- **WHEN** o peso não foi informado
- **THEN** o campo exibe “Não informado” sem sufixo Kg
