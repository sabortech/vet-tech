## Why
O clique na mascote ainda não abre interface. Implementar o chat aprovado como pop-up com fundo escurecido.
## What Changes
- Chat global responsivo, modal acessível, campo de mensagens e chips.
- Reutilizar evento público da mascote, preservando animações.
- Orientações locais, sem simular consultas ao prontuário ou disponibilidade de atendimento humano.
## Capabilities
### New Capabilities
- `support-chat`: painel de suporte local.
### Modified Capabilities
- `floating-mascot`: evento de clique passa a abrir o painel.
## Impact
Wrapper global, assets JS/CSS e testes de navegador. Nenhuma API, dependência ou dado clínico novo. RF01/RF02: orientação de navegação; autorização backend existente preservada. Sem notificações.

## Conversas e identidade
Cada abertura inicia conversa limpa; saudação usa nome confirmado na sessão ou texto genérico para visitante. Botão Histórico permite consultar conversas anteriores nesta aba. Histórico só em memória; mudança de identidade/login/logout apaga todas as conversas para não misturar usuários, sem expor token.
