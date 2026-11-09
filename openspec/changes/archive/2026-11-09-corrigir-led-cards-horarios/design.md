# Design

## Contexto
Ajuste localizado na apresentação existente; motivação em proposal.md.

## Decisão
Reutilizar perimeter_led e consultation_status_led no contorno do cartão, com tokens existentes. CSS realiza a circulação em 8 segundos e 20 segundos com movimento reduzido, sem chamadas ao backend.

## Risco e verificação
SVG absoluto poderia bloquear ações; pointer-events:none e verificação de cliques mitigam o risco. Resultados em verification.md.

## Entrega
Sem migração de dados. Reversão pelo commit da interface.
