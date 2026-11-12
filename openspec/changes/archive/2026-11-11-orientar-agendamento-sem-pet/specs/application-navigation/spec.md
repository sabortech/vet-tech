## ADDED Requirements

### Requirement: Convite de agendamento sem pet selecionado
Todas as seções clínicas que compartilham a orientação sem pet SHALL exibir “Gostaria de agendar uma consulta?” abaixo do botão existente. O convite SHALL abrir um painel com tartaruga e dois cards lado a lado em telas largas, adaptados sem corte em telas estreitas, nos temas claro e escuro.

#### Scenario: Abrir painel de escolha
- **WHEN** o tutor clica no convite sem pet selecionado
- **THEN** vê opções de selecionar pet existente em Mudar pet e cadastrar novo em Meus Pets

#### Scenario: Selecionar pet existente
- **WHEN** o tutor clica no card de pet existente
- **THEN** navega à lista de Mudar pet pelo fluxo existente

#### Scenario: Cadastrar pet
- **WHEN** o tutor clica no card de novo pet
- **THEN** navega a Meus Pets com o formulário de cadastro existente

#### Scenario: Cancelar orientação
- **WHEN** o tutor fecha o painel ou usa Escape
- **THEN** permanece na seção sem selecionar pet ou criar consulta
