# Design

## Context
O chat global é construído em assets/support-chat.js e estilizado em assets/support-chat.css. O vídeo local possui 1280 × 720 e oito segundos.

## Goals / Non-Goals
Exibir um banner compacto abaixo do cabeçalho para todos os perfis. Preservar mensagens, histórico, tema, LED e transporte existentes.

## Decisions
Usar vídeo HTML nativo com autoplay, muted, loop e playsInline, sem controles. Banner de 112px com object-fit:contain para preservar a arte inteira, fundo do tema e borda discreta. Pausar ao fechar; retomar ao abrir, tratando rejeição de play sem erro de console. Manter mensagens roláveis e campo de envio acessível.

## Risks / Trade-offs
Autoplay depende do navegador; muted e playsInline permitem reprodução nos navegadores usuais. Verificar decodificação e repetição reais no Chromium.

## Verification
Conferir ordem visual, avanço e retorno do tempo após oito segundos, pausa/reabertura, temas claro/escuro e viewport móvel sem enviar mensagens à IA.

O banner é irmão do log e do histórico no flex vertical, sem encolher: permanece sempre ao topo enquanto apenas o conteúdo abaixo rola.
