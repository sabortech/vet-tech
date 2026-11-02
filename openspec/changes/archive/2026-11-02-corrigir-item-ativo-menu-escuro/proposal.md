# Proposal

## Why
Botões do menu médico usam o token escuro de superfície no item ativo, enquanto links como Configurações mantêm o destaque claro. Isso prejudica contraste e consistência.

## What Changes
- Unificar a regra de item ativo para links e botões em todos os perfis.
- Manter fundo branco/texto verde escuro, com hover/foco claro consistente.
- Remover regras conflitantes específicas de botões.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
Nenhuma: correção da implementação do destaque branco já exigido por application-navigation. skip_specs: true.

## Impact
Somente CSS compartilhado da sidebar. Sem mudanças em navegação, dados, autenticação ou regras de acesso.
