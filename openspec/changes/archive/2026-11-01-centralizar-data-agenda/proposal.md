# Proposal

## Why
A data acima dos dias da semana fica centralizada apenas no espaço restante após os controles, deslocada para a esquerda em relação ao calendário.

## What Changes
- Centralizar a navegação de data na largura total do calendário com colunas laterais simétricas.
- Manter Hoje e calendário à direita quando houver espaço e em linha separada quando necessário, sem sobreposição.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
Nenhuma. Ajuste estritamente visual; `skip_specs: true`.

## Impact
Somente CSS isolado da agenda veterinária. Sem mudanças em eventos, dados, autenticação, auditoria ou notificações. Verificação por geometria no navegador em desktop, menu recolhido e celular.
