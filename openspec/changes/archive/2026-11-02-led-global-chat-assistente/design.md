# Design

## Context
O chat é um dialog nativo criado uma vez por assets/support-chat.js e reutilizado em todas as páginas, com tema global. O calendário já usa segmento SVG normalizado.

## Goals / Non-Goals
Reproduzir o mesmo efeito no chat sem alterar transporte, histórico, autenticação ou comportamento da mascote.

## Decisions
Criar um SVG decorativo com createElementNS no build único do chat, com rect pathLength=100 e dimensões relativas. CSS exclusivo vt-chat-led posiciona sobre a borda com pointer-events:none e sem tamanho no flex. Animar dashoffset 0/-100, traço14/espaço86, período6s/12s. Somente dialog[open] anima. Raio desktop acompanha 24px e raio móvel fica zero, preservando fullscreen. Mantém-se o comportamento de movimento reduzido das outras animações.

## Risks / Trade-offs
Borda não deve interferir nos botões ou rolagem → testar mensagens, histórico, fechar/reabrir e dimensões do chat. Independência de perfil é garantida pela composição global, validada também nos contextos de visitante/tutor/médico.
