# Tasks

## 1. Preenchimento circular localizado

- [x] 1.1 Ajustar em `assets/vet_tech.css` o padding e as dimensões dos wrappers e avatar sob `.vet-schedule-avatar-frame`, com recorte circular centralizado e proporcional; verificar em navegador fotos horizontais, verticais e quadradas cobrindo a área interna e a moldura mantendo 52 × 52 px.
- [x] 1.2 Verificar em desktop e celular, nos temas claro/escuro, que o LED e halo permanecem na borda, com cores por status e movimento horário; comparar instantes distintos e confirmar desaceleração com movimento reduzido. Registrar capturas e resultados em `verification.md` e `evidence/` desta mudança.

## 2. Regressão integrada

- [x] 2.1 Executar a verificação existente `tests/integration/schedule_status_colors_browser.py` conforme seu ambiente de preview e conferir foto ausente, imagem inválida e acesso revogado; registrar os comandos, resultados e eventuais limites em `verification.md`.
- [x] 2.2 Conferir abertura de Histórico e início/retomada da consulta pelos controles existentes e comparar avatares de Consultas e resumo do paciente; registrar evidência de ações funcionais e ausência de alteração visual fora de Horários em `verification.md`.

## 3. Retrato do histórico anterior

- [x] 3.1 Remover a folga do retrato de histórico com CSS restrito a `.history-profile-portrait`, corrigindo baseline e recorte proporcional; verificar círculo de 120 px em desktop e 110 px no celular, com preenchimento interno completo, temas e proporções variadas, registrando evidências.
- [x] 3.2 Conferir categorias, fechamento e estados sem foto/erro no histórico sintético após o ajuste, preservando controles e LED de Horários; registrar resultados em `verification.md`.
