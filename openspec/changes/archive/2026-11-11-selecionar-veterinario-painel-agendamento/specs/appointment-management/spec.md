## ADDED Requirements

### Requirement: Tutor escolhe o médico no painel inicial de agendamento
O sistema SHALL oferecer no painel inicial do calendário seletores de pet e veterinário identificado pelo nome, carregando somente profissionais cadastrados compatíveis com a espécie do pet próprio. Avançar SHALL exigir pet e profissional válidos. A confirmação SHALL mostrar o pet e médico escolhidos, motivo e aviso de liberação prévia do prontuário.

#### Scenario: Agendamento com médico escolhido
- **GIVEN** tutor autenticado selecionou seu pet
- **WHEN** escolhe médico cadastrado compatível, dia e horário e avança
- **THEN** a confirmação mostra pet e médico escolhidos e preserva o vínculo no envio

#### Scenario: Troca do pet
- **WHEN** o tutor troca o pet durante o agendamento
- **THEN** o médico anterior é limpo e somente a resposta do catálogo do pet atual pode preencher a lista

#### Scenario: Lista indisponível ou vazia
- **WHEN** não há profissionais disponíveis ou a leitura falha
- **THEN** a mensagem é apresentada e o tutor não avança sem escolher profissional válido

#### Scenario: Pets com médicos diferentes
- **GIVEN** tutor agenda um pet com médico A e outro pet com médico B
- **WHEN** cada médico consulta sua agenda e prontuário
- **THEN** a consulta é atribuída ao médico escolhido e o acesso ao prontuário exige autorização vigente para aquele pet, mantendo auditoria existente
- **AND** o pet pode ser agendado com outro médico em consulta futura
