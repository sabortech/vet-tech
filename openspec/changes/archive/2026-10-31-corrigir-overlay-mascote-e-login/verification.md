# Verificação — 31/10/2026

## Causas confirmadas

A faixa visual vinha de `.mascote-app`: altura da viewport menos 208/160 px,
overflow auto e altura do login recalculada para caber nessa reserva.
O wrapper agora é Fragment: não existe elemento HTML extra de layout.
A mascote permanece fixed, como irmã do outlet em extra_app_wraps.
O painel voltou a min(92vh,708px) no desktop e o fundo cobre a viewport.

O login falhava na comunicação frontend/backend local: dois `reflex run` de
mesmo projeto serviam frontends em 3000/3001, sem listener de backend na 8000.
O Chromium registrou repetidos erros de conexão a ws://localhost:8000/_event;
o formulário não chegava ao handler. A origem real do Xano estava no .env.
Uma autenticação direta e a confirmação da identidade retornaram HTTP 200.
Não foi necessário alterar conta, senha ou lógica de autorização.

## Correção operacional

Interrompidos somente os launchers e frontends cujo PID/cwd foram identificados
como pertencentes a /home/usuario/vet-tech. Após SIGINT não liberar as portas,
os frontends correspondentes receberam SIGTERM. Nenhum navegador foi encerrado.
Uma única instância de produção foi iniciada em http://localhost:3001 com
scripts/run-local.sh, que carrega .env e executa frontend/backend juntos.
Logs em reflex.log; nenhuma senha/token foi escrita em código ou artefatos.
A instância corrigida permanece executando para o usuário.

## Resultados

- Compile dry e build de produção aprovados; bash -n e node --check aprovados.
- 152 testes unitários existentes aprovados.
- Teste real de login no Chromium com credenciais fornecidas somente no ambiente:
  login_success=true, global_mascot_persisted=true, layout_unchanged=true.
  Confirmada navegação para Configurações e Meus Pets após autenticação real.
  Não foram persistidas capturas autenticadas, senha, tokens ou dados de conta.
- Teste anônimo de regressão em http://localhost:3001: login e cadastro a 390/1366
  px mantêm posição/tamanho do conteúdo e altura do documento exatamente iguais
  com a mascote visível ou oculta. Não existe .mascote-app no DOM.
- Mascote presente nas seis rotas; navegação pública mantém o mesmo nó DOM.
- Teclado, toque, reduced-motion, aba oculta, RGB, fallback de imagem e de hover
  aprovados. Zero eventos de movimento ao backend e zero leituras geométricas
  dentro do RAF; loop estável após convergir; maior callback de aproximadamente
  0,3 ms nesta rodada, sem garantia de hardware universal.
- Botão 160×160 desktop e 112×112 mobile, offsets 24 px; proporção preservada.
- Fundo do login cobre toda a viewport e painel aparece centralizado em captura.

Comando anônimo reproduzível (requer Playwright instalado):

```bash
PYTHONPATH=/tmp/vet-tech-mascote-tools .venv/bin/python tests/integration/mascote_browser.py --url http://localhost:3001 --evidence /tmp/mascote-overlay-evidence --chromium /home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome
```

O teste real reutilizável está em tests/integration/run_mascote_login_live.py e
recebe VET_TECH_TEST_EMAIL/VET_TECH_TEST_PASSWORD do ambiente, nunca do repositório.
Capturas anônimas e resultados estão em evidence/. Contas protegidas e dados
clínicos não foram modificados. O overlay pode cruzar conteúdo durante rolagem,
mas não ocupa espaço no fluxo; essa é a mudança solicitada em relação à faixa.
Chat permanece fora de escopo.
