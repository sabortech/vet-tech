# Design

## Context
A imagem transparente fornecida representa a tartaruga espreitando por uma borda à direita. O diálogo já tem divisória vertical em desktop e horizontal em celular.

## Goals / Non-Goals
Trocar somente a decoração e sua posição; preservar controles, seleção de datas e luz verde da janela.

## Decisions
Usar posicionamento absoluto relativo ao painel lateral, centralizado verticalmente na divisória. Compensar a margem transparente do PNG para alinhar o corpo à borda; manter mão visível no pequeno espaço interno, sem alcançar os dias. Aplicar pointer-events:none e alt vazio. No celular manter dimensão compacta junto à extremidade da divisória horizontal.

## Risks / Trade-offs
Risco de cobrir datas em telas menores → revisar limites da imagem, datas clicáveis e screenshots em desktop/celular.
