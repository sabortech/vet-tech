# Verificação

- SVG decorativo adicionado ao build único do diálogo global do chat.
- Segmento 14/espaço 86, pathLength=100, movimento horário linear de 6s; reduce 12s.
- CSS ativa animação somente com dialog[open]; fechar/minimizar deixa de animar.
- Desktop preserva raio 24px, celular raio 0 e fullscreen. Overlay sem foco e
  pointer-events:none não interfere em mensagens, histórico ou ações.
- node --check assets/support-chat.js e build de produção passaram; aplicação
  atualizada na porta 3000.
- tests/integration/led_chat_theme_browser.py verificou avanço temporal do
  traço, durações normal/reduzida, parada ao fechar, reabertura, conversa,
  histórico e troca de tema nos perfis visitante, tutor e veterinário.
- Página de cadastro e celular390×844 também passaram, sem overflow, mantendo
  dimensões fullscreen. Nenhuma exceção JavaScript.
- Transporte do chat simulado apenas no teste; nenhuma chamada à IA/n8n.
  Logins utilizaram somente fixtures de desenvolvimento. Nenhum dado alterado.
- Capturas e results.json em evidence/. OpenSpec estrito, spec principal e
  git diff --check validados.
