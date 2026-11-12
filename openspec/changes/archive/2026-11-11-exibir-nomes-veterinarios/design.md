## Context
O histórico retorna IDs sem nomes; alguns componentes usam o ID como alternativa. Consultas do tutor já possuem left join do profissional.

## Goals / Non-Goals
Exibir nomes em todos os campos profissionais, mantendo IDs para vínculos e ações.

## Decisions
Reutilizar left join de veterinario com projeção apenas de nome, preservando filtros e autorização. Propagar nome da evolução à doença consolidada. Usar alternativa textual para vínculos ausentes. Acrescentar nome ao DTO PDF sem remover seu ID interno.

## Risks / Trade-offs
As alterações Xano precisam ser publicadas no backend utilizado para disponibilizar os nomes. Enquanto não houver nome, exibir alternativa textual.
