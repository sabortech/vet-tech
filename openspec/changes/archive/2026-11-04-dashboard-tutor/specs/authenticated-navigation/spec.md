## MODIFIED Requirements

### Requirement: Menu retrátil preserva o contexto
O sistema SHALL exibir Dashboard, Prontuário, Vacinas, Medicamentos, Doenças e Consultas nessa ordem, com Novo pet e Mudar pet na parte inferior. O Dashboard SHALL ser um destino distinto do Prontuário. O menu SHALL recolher e expandir sem alterar o pet ativo; o escopo selecionado no Dashboard SHALL NOT alterar essa seleção clínica. A seção ativa e o pet atual SHALL ser identificáveis, com nomes acessíveis e operação por teclado em desktop e celular.

#### Scenario: Recolher menu
- **WHEN** o tutor recolhe e expande o menu com um pet aberto
- **THEN** o pet continua selecionado e os controles permanecem identificáveis e utilizáveis

#### Scenario: Alterar escopo no Dashboard
- **GIVEN** o tutor possui um pet selecionado no prontuário
- **WHEN** altera o filtro do Dashboard entre “Todos os pets” e um pet específico
- **THEN** a seleção do prontuário não é alterada e o escopo do Dashboard é identificável

#### Scenario: Celular
- **WHEN** o tutor navega em uma tela estreita
- **THEN** consegue alcançar menu, conteúdo e ações inferiores sem corte ou rolagem horizontal
