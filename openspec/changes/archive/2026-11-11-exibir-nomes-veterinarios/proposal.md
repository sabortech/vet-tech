## Why
Campos clínicos exibem o ID do veterinário, dificultando sua identificação.

## What Changes
- Retornar o nome nas leituras autorizadas e exibi-lo nos cartões, acessos e PDF.
- Preservar IDs internos e mostrar “Nome não informado” se o vínculo não tiver nome.

## Capabilities
### Modified Capabilities
- `clinical-records`: identificação nominal do profissional nos registros.

## Impact
Reflex, projeção PDF e consultas Xano. Dados de saúde continuam sob as mesmas autorizações e auditoria; somente o nome profissional é acrescentado. Sem impacto em notificações.
