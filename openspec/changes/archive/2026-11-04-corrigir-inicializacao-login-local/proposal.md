# Proposal

## Why
A instância em localhost:3000 serve a tela, mas tenta conectar eventos à porta 8000 sem backend escutando. Nenhuma tentativa de login chega ao Xano.

## What Changes
- Corrigir a porta padrão do launcher local para 3000 com frontend e backend juntos.
- Documentar a inicialização e restaurar o processo local usando o launcher existente.
- Verificar conexão de eventos e resposta de autenticação no navegador.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
Nenhuma. Correção operacional de inicialização; contratos de autenticação permanecem existentes. `skip_specs: true` por se tratar de tooling.

## Impact
Launcher, documentação e processo local Reflex. Sem alterações em credenciais, dados clínicos, autorização, auditoria ou notificações.
