# Proposal

## Why
A luz da janela de calendário não está circulando na aplicação real, e o chat flutuante usa cores claras fixas mesmo com preferência escura.

## What Changes
- Corrigir a animação contínua da luz verde somente na borda do calendário aberto, no sentido horário.
- Aplicar os tokens globais de tema a todas as superfícies do chat, incluindo histórico, mensagens, ações e campo de texto.
- Seguir a preferência antes da abertura e durante mudanças de tema em todas as páginas/perfis; preservar chat e transporte existentes.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `interface-preferences`: explicitar o chat global no contrato de tema coerente, incluindo atualizações enquanto aberto.
A luz do calendário já está especificada; esta change corrige sua implementação.

## Impact
CSS de calendário/chat e verificação em navegador da aplicação real. Sem alterações em dados, autenticação, APIs, mensagens, n8n ou permissões. Sem envio de informações clínicas nos testes.
