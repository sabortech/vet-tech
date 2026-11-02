## ADDED Requirements

### Requirement: Seletores de mês e ano com abertura inferior
O sistema SHALL apresentar seletores de mês e ano no diálogo do calendário com cores e cantos do sistema e chevron apontado para baixo. As opções SHALL abrir somente abaixo do acionador, com altura limitada e rolagem interna; SHALL preservar operação por teclado, seleção ativa e adaptação aos temas claro/escuro e ao celular.

#### Scenario: Abrir lista de mês ou ano
- **WHEN** o veterinário aciona um dos seletores
- **THEN** a lista aparece abaixo do controle, sem reposicionamento para cima, e permite alcançar as opções por rolagem e teclado

#### Scenario: Selecionar opção
- **WHEN** o veterinário escolhe mês ou ano
- **THEN** a grade mensal atualiza sem alterar a data da agenda antes da seleção explícita de um dia
