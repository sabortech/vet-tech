# Design

## Context
O CSS anterior definia animation:none e stroke-dasharray:none sob prefers-reduced-motion, resultando em borda totalmente acesa e estática. O percurso SVG já foi validado na aplicação real.

## Goals / Non-Goals
Garantir o movimento solicitado sem alterar composição, dados ou demais preferências de animação do sistema.

## Decisions
Preservar SVG normalizado em 100 unidades e dasharray14/86. Usar ciclo linear de 6s, com extremidades equivalentes 0/-100 para loop sem salto. Para reduce usar 12s e manter o segmento, sem desabilitar a animação. Testar avanço em tempo real e passagem pelo limite do ciclo com ambos os modos. Pausas de captura ficam apenas em contextos de teste descartáveis e são explicitamente retomadas.

## Risks / Trade-offs
Movimento reduzido agora desacelera este efeito decorativo, em vez de congelá-lo, conforme a solicitação explícita. Não alterar regras de movimento de outros componentes.
