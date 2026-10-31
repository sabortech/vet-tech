# Verificação inicial — 31/10/2026 (histórico)

## Ambiente e comandos

Reflex 0.9.11, build de produção, Chromium headless local e stub Xano sintético
existente em `tests/integration/pet_loading_browser.py`. Nenhum dado real usado.
Playwright instalado somente em `/tmp/vet-tech-mascote-tools` para esta execução.

```bash
.venv/bin/reflex compile --dry
node --check assets/mascote.js
.venv/bin/python -m unittest discover -s tests/unit
openspec validate add-mascote-flutuante --strict
PYTHONPATH=/tmp/vet-tech-mascote-tools .venv/bin/python tests/integration/mascote_browser.py --authenticated --chromium /home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome
```

Servidor QA iniciado com `XANO_API_BASE_URL=http://127.0.0.1:9010` e
`reflex run --env prod --single-port`. Instalação do Playwright, abertura das portas
locais e execução do Chromium exigiram execução fora do sandbox. Logs em `/tmp`.

## Resultados

- Compilação seca e build de produção aprovados; JavaScript válido.
- 152 testes unitários existentes aprovados.
- OpenSpec strict aprovado.
- Montagem única do botão nas seis rotas registradas, incluindo rota dinâmica.
  Navegação pública e navegação autenticada de tutor mantêm exatamente o mesmo
  nó DOM da mascote.
- Zero eventos WebSocket de aplicação por movimento do cursor no app real.
- Instrumentação isolada da mesma árvore DOM: um listener pointermove mesmo
  após carregar o script duas vezes; zero getBoundingClientRect durante RAF;
  contagem de frames estável após convergência; maior callback medido de 0,5 ms
  nesta rodada (não é uma garantia para outros dispositivos).
- Cabeça/corpo alinhados após corrigir o recorte dos pixels quase transparentes
  nas bordas da arte gerada. Olhos SVG e piscadas inspecionados.
- Hover, foco visível, Enter/Espaço, toque real via protocolo do Chromium,
  clique único, glow RGB limitado ao glow, fallback de imagem e alteração
  dinâmica de reduced-motion aprovados. Visibilitychange simulado pausa o loop.
- Separação física entre scrollport e botão, sem colisões com controles visíveis,
  em login/cadastro (início e fim da rolagem) a 390/1366 px e em Meus Pets,
  Configurações/Prontuário a 390/768/1366 px. Toaster recebe offset acima da faixa.

Os PNGs RGBA têm 260×260 px e aproximadamente 121 KB no total. São derivados
das referências fornecidas; procedência e alinhamento descritos no README dos
assets. Ver `evidence/results.json` e capturas para resultados detalhados.

## Limites e pendências

Testes em emulação, sem medição de GPU em dispositivo físico. Acesso a atendimento
foi exercitado com os guards e o wrapper global; não se abriu consulta clínica
real nem se validou conteúdo médico. O scrollport compartilhado evita colisão
também nas páginas protegidas sem mudar regras de acesso.

O CLI avisa que o bloco preexistente `rules.rules` em `openspec/config.yaml` não
é uma lista de regras; a configuração não foi alterada nesta change. Os artefatos
seguem as restrições de projeto aplicáveis, inclusive documentação em português.

Chat continua fora do escopo. O único contrato de integração entregue é o evento
`vettech:mascote-click`; nenhum painel, serviço, estado ou consumidor foi adicionado.


# Correção de proporção, imagem inteira e fundo — 31/10/2026

Esta revisão substitui a composição segmentada descrita na verificação inicial.
Dimensões conferidas antes do CSS: turtu.png original 372×671 RGBA, com uma
única tartaruga e sombra oval. Usuário autorizou remoção da sombra e canvas
quadrado. Ferramenta integrada de edição gerou uma tartaruga sem sombra em
1254×1254 RGBA; redução uniforme para mascote_idle.png de 320×320 RGBA
(70.528 bytes). Hover e camadas históricas: 260×260 RGBA. As camadas antigas
não são mais usadas. Prompt e procedência estão em assets/mascote/README.md.

A deformação anterior foi incorporada ao bitmap ao redimensionar separadamente
largura/altura das camadas. object-fit contain preservava o canvas, mas não
recuperava a proporção da arte já deformada. A faixa inferior vinha da reserva
de espaço do wrapper, que deixava parte da viewport fora do fundo do login.
Agora a camada de fundo do login é fixed/cover; html/body/root usam min-height
100dvh. O painel foi ajustado à altura disponível sem cortar as bordas.

Comandos da verificação atual:

```bash
.venv/bin/reflex compile --dry
node --check assets/mascote.js
openspec validate add-mascote-flutuante --strict
PYTHONPATH=/tmp/vet-tech-mascote-tools .venv/bin/python tests/integration/mascote_browser.py --url http://localhost:3001 --authenticated --chromium /home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome
```

Build de produção, sintaxe JS e OpenSpec aprovados. Porta 3000 já estava ocupada;
QA executado na 3001, sem interromper o servidor preexistente. Stub local sintético.
Os testes do navegador confirmaram: botão 160×160, aspect-ratio 1, imagem com
razão natural/renderizada 1 e object-fit contain, offsets 24 px, mobile 112 px,
rastreamento da imagem inteira, um listener passivo, RAF parado ao convergir,
zero leituras geométricas dentro do RAF e zero eventos de movimento ao backend.
Maior callback nesta rodada: aproximadamente 0,3 ms. Teclado, toque, reduced-motion,
visibilitychange, RGB, ausência de hover mantendo idle e fallback geral aprovados.
Navegação preserva o mesmo nó; colisões mantêm resultado zero nas larguras testadas.
Fundo fixed cobre de -36,72 a 936,72 px em viewport de 900 px; capturas desktop/mobile
conferidas. Resultados e capturas atuais em evidence/correcao-proporcao/.

Chat continua pendente. Piscar e rastreamento segmentado ficam suspensos enquanto
usar o asset único, conforme a revisão solicitada. Limites de QA da execução
inicial continuam aplicáveis: emulação de dispositivos e dados clínicos sintéticos.
