# Verificação

## Diagnóstico
O calendário real possuía animação de ângulo ativa, mas o gradiente longo e
suave não tornava a circulação suficientemente perceptível. O chat usava
background #f4f5f7 mesmo com html[data-vt-theme=dark], comprovado no navegador.

## Correção
- Segmento SVG arredondado com pathLength=100, dasharray 14/86 e deslocamento
  de 0 para -100 percorre toda a borda no sentido horário. SVG não recebe cliques.
- Redução de movimento conserva borda estática; somente o pop-up recebe o efeito.
- Todas as superfícies/textos do chat usam tokens globais, incluindo usuário,
  assistente, histórico, ações, envio, campo, placeholder e legenda.
- Não houve mudança de transporte, autenticação, n8n, APIs ou dados.

## Verificações executadas
- Todas as páginas compilaram; build de produção e atualização das instâncias
  localhost:3000 e localhost:3015 concluídos.
- tests/integration/led_chat_theme_browser.py verificou a aplicação real com
  contas sintéticas de tutor e veterinário, além de visitante e cadastro.
- Deslocamento do traço medido em tempo real e quatro posições capturadas ao
  redor do retângulo: evidence/theme/led-quarter-{0,1,2,3}.png.
- Temas claro e escuro do chat foram comparados com os tokens esperados para
  painel, texto, formulário, cabeçalho e bolhas; troca durante conversa preserva
  mensagens. Histórico também acompanha o tema. Preferências reais ativaram
  o modo escuro nos dois perfis. Celular mantém chat fullscreen.
- O transporte do chat foi interceptado somente no roteiro de teste; nenhuma
  pergunta foi enviada à IA/n8n. Logins usaram exclusivamente fixtures de
  desenvolvimento, sem editar contas ou senhas.
- tests/integration/veterinary_schedule_browser.py passou com o novo traço:
  datas, foco, seleção, consentimento, paginação, menu, desktop/celular e tema.
- Nenhuma exceção JavaScript. Resultados JSON e capturas em evidence/.
- OpenSpec estrito, specs principais e git diff --check validados.
