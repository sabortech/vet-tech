# Proposal

## Why

As mensagens enviadas nas conversas entre tutor e veterinário ficam visualmente indistintas do fundo do chat. No assistente, o vídeo do banner continua ocupando espaço visível depois do primeiro envio e durante o restante da conversa.

## What Changes

- Dar aos balões enviados um fundo sólido e opaco, distinguível do fundo da conversa em tema claro e escuro, tanto em atendimentos quanto em mensagens diretas.
- Mostrar mensagens enviadas ao bot como Entregue enquanto aguardam resposta e mudar para Visto quando o bot responder com sucesso.
- Ocultar o banner de vídeo após o primeiro envio do tutor ao assistente e mantê-lo oculto enquanto aquela conversa continuar.
- Restaurar o banner ao iniciar uma nova conversa com o assistente.
- Versionar a URL do script do chat para que navegadores carreguem a implementação atualizada após o build.

## Capabilities

### New Capabilities

### Modified Capabilities
- `support-chat`: exigir balões enviados opacos durante atendimentos e recibos de Entregue/Visto nas conversas com o bot.
- `direct-messaging`: exigir balões enviados opacos e distinguíveis em conversas privadas entre tutor e veterinário.
- `assistant-chat-banner`: definir a visibilidade do vídeo após o primeiro envio e sua restauração em uma nova conversa.

## Impact

- Interface: `assets/support-chat.css`, `assets/support-chat.js` e referência ao script em `vet_tech/vet_tech.py`.
- Especificações OpenSpec de conversas humanas, mensagens diretas e banner do assistente.
- Sem alterações a dados, APIs, autorização clínica, notificações ou dependências.
