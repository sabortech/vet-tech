# Verificação

## Entrega
Somente Hoje e o ícone de calendário aparecem na barra. O ícone abre janela
ampla com mês/ano, dias selecionáveis e tartaruga do asset existente. A luz verde
percorre somente as bordas dessa janela no sentido horário; botões não recebem
animação. A preferência de movimento reduzido mantém borda estática.

## Verificações
- Reflex compilou todas as páginas e o build de produção passou.
- 50 testes unitários de agenda, estado clínico, projeção Xano, navegação e
  autorização passaram. Novos cenários: navegar/cancelar sem request ou mudança
  de data; ano bissexto; virada de ano e limites 1/9999; seleção passada fecha
  diálogo e volta à página 1; limpeza de sessão e guard de perfil.
- Playwright na prévia isolada de dados sintéticos: janela, tartaruga, seleção,
  navegação, Escape, foco dentro e retorno ao ícone; vazio/erro, paginação,
  consultas, sidebar e menu do tutor preservados. Nenhuma exceção JavaScript.
- Animação verificada pelo avanço positivo do ângulo CSS, em sentido horário.
  Hoje e ícone com animationName=none; somente janela com vet-date-border-orbit.
- Desktop 1440×1000 e celular 390×844; temas claro/escuro; conteúdo sem overflow
  horizontal, modal responsivo e movimento reduzido sem animação.
- Evidências em evidence/, incluindo calendar-desktop.png,
  calendar-mobile.png e calendar-mobile-dark.png.
- Aplicação atualizada em http://localhost:3000/ e prévia em
  http://localhost:3015/. Nenhum dado real foi criado ou modificado.
- Nenhuma mudança no backend nesta entrega. A publicação da foto da agenda,
  registrada na change anterior, permanece independente desta alteração.
- OpenSpec estrito, especificações principais e git diff --check validados.
