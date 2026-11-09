# Design

## Contexto
Ajuste localizado na apresentação existente; motivação em proposal.md.

## Decisão
Reutilizar attendance_history_dialog com condição de status finalizada dentro do bloco autorizado. Usar classe compartilhada para igualar dimensões de Exportar PDF e Ver Histórico anterior, mantendo o texto em uma linha.

## Risco e verificação
Texto longo poderia causar overflow; coluna de ações ajustada e verificação em desktop/celular mitigam o risco. Resultados em verification.md.

## Entrega
Sem migração de dados. Reversão pelo commit da interface.
