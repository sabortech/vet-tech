# Verificação

- Composição Radix dos seletores, chevron-down explícito, cores e cantos
  consistentes com a agenda; indicadores de seleção sem sobrepor texto.
- Reflex compile --dry e builds de produção passaram; aplicação atualizada
  na porta 3000 e prévia sintética na 3015.
- Playwright mediu data-side=bottom e a posição da lista abaixo do limite
  inferior do respectivo botão em 1440×1000, 390×844 e 390×600.
- Mês e ano com altura limitada e rolagem; seleção de mês e navegação anual
  por teclado (End/Enter) passaram, sem alterar data ativa antes de escolher dia.
- Escape retorna foco ao acionador; temas claro/escuro verificados, sem
  exceções JavaScript. Screenshots e results.json em evidence/.
- Somente componentes/CSS dos seletores modificados; sem operações de dados.
- OpenSpec estrito, especificações e git diff --check validados.
