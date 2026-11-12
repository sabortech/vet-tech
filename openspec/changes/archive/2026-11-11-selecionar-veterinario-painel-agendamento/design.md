## Context
O Dashboard já carrega profissionais ao abrir o agendamento de um pet. O seletor só aparece na segunda etapa. A API filtra profissionais cadastrados pela espécie e valida propriedade do pet.

## Goals / Non-Goals
Exibir a seleção no painel inicial e preservar agendamentos independentes por par pet/médico. Não criar médico fixo ou alterar autorizações existentes.

## Decisions
Mover seletores para a primeira etapa, reutilizando handlers e catálogo atual. Bloquear avanço sem profissional pertencente à lista atual. Limpar profissional ao trocar pet e preservar proteção contra respostas fora de ordem. Usar resumos nominais na segunda etapa e preservar aviso de consentimento. Desabilitar seletores durante envio ou resultado incerto.

## Risks / Trade-offs
Somente médicos compatíveis cadastrados aparecem; lista vazia ou falha de leitura exige seleção válida antes de avançar. O painel existente permite rolagem em telas baixas.
