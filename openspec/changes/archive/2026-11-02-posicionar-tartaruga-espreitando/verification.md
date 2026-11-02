# Verificação

- Imagem atual removida do componente e substituída por /espreitando.png.
- Desktop: imagem 180×270 px, centralizada na divisória; a margem transparente
  foi compensada para alinhar o corpo à linha, com a mão visível sem cobrir dias.
- Celular: decoração compacta 86×129 px, sem ultrapassar a janela.
- Imagem decorativa, alt vazio e pointer-events:none preservam os cliques.
- Reflex compile --dry e build de produção passaram.
- Revisão Playwright com os componentes reais e dados sintéticos: seleção de
  data, mês, foco/Escape, luz da janela, desktop/celular e tema escuro.
- Capturas e resultado do navegador em evidence/.
- Aplicação e prévia recarregadas nas portas 3000 e 3015.
- Nenhuma operação de dados ou modificação de backend nesta correção.
