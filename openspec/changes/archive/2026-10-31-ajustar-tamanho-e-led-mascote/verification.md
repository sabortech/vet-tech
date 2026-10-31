# Verificação — 31/10/2026

Botão reduzido para 140×140 desktop e 96×96 mobile, mantendo proporção,
offsets de 24 px, overlay global e geometria das páginas.

Glow CSS executa apenas uma sequência de 4 segundos: dois picos suaves
em 1 s e 3 s; em 4 s assenta na opacidade .75 e fica estável até a saída.
Somente opacity e transform são animados. Nenhum timer JS foi acrescentado.

Build de produção do Reflex e validação estrita OpenSpec aprovados.
App reiniciado com scripts/run-local.sh na porta 3001 e mantido executando.

Teste Chromium de tests/integration/mascote_browser.py aprovado. Curva medida
pela Web Animations API nos tempos 0/1/2/3/4 s: 0/.95/.12/.95/.75; duração
4000 ms e uma única execução. Confirmada finalização da animação, LED constante,
saída apagando e nova entrada reiniciando. Foco de teclado, toque, reduced-motion
com luz estática, aba oculta, RGB e fallbacks aprovados. O teste aguarda o
crossfade antes de conferir a pose feliz, evitando leitura durante a transição.

Navegação mantém o mesmo nó, geometria permanece igual com/sem botão em
390/1366 px, zero eventos de movimento ao backend, zero leituras de geometria
no RAF e parada após convergência. Maior callback medido: cerca de 0,3 ms.
Capturas e resultados anônimos estão em evidence/; nenhum dado de conta usado.

Comando da execução:

```bash
PYTHONPATH=/tmp/vet-tech-mascote-tools .venv/bin/python tests/integration/mascote_browser.py --url http://localhost:3001 --evidence /tmp/mascote-led-evidence --chromium /home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome
```


## Refinamento: intensidade reforçada

Halo ampliado para 116% do canvas com gradiente verde mais opaco. Intensidade
final aumentada de .75 para .95, picos para 1 e vale para .16, mantendo dois
picos em quatro segundos e o brilho constante ao final. Não mudou o tamanho,
a área de clique, o layout ou o JavaScript da mascote.

Recompilação e startup de produção em localhost:3001 aprovados. Regressão
Chromium aprovada: curva [0,1,.16,1,.95], uma execução de 4000 ms; saída,
reentrada, teclado/toque/reduced-motion e todos os demais checks preservados.
Captura `evidence/intensidade/led-login.png` inspecionada: halo verde claramente
visível sobre o fundo do login. Dados atuais em evidence/intensidade/results.json.
Validação estrita OpenSpec e git diff --check aprovados. Esta seção substitui
as intensidades citadas no teste inicial acima. Servidor permanece executando.


## Reversão solicitada pelo usuário

Desfeito somente o reforço de intensidade: gradiente original, halo de 100% e
opacidade final .75, mantendo 140/96 px e duas pulsações em 4 s. Build de produção
aprovado e aplicação reiniciada na porta 3001. Chromium confirmou após 4,25 s:
opacidade .75, halo e botão ambos de 140 px, uma execução e gradiente original
(com alpha central serializado pelo navegador como .66). Esta reversão substitui
o refinamento de intensidade descrito acima. Docs e expectativas de teste
restauradas; nenhuma mudança em login, JS ou layout.
