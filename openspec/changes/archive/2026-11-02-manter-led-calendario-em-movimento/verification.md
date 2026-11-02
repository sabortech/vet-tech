# Verificação

- Removida a regra que convertia o traço em borda inteira estática no modo reduce.
- Ciclo normal: 6s, linear, infinito. Movimento reduzido: 12s, mantendo o segmento.
- Verificado no Chromium por tests/integration/led_continuous_browser.py sem
  pausar, acelerar ou reposicionar a animação: voltas completas de ambos os modos
  em 1100×900 e 390×844, com avanço horário positivo em todos os intervalos e
  passagem pelo fim do ciclo sem parada. Total de 156 amostras temporais.
- O teste confirmou também que localhost:3000 serve o CSS de 6s/12s atualizado.
- Capturas e dados em evidence/results.json. Regras de outras animações e do
  chat permanecem preservadas.
- Aplicação recompilada e recarregada em produção local.
- OpenSpec estrito, spec principal e git diff --check validados.
