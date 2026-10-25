# Tasks

## 1. Carregamento por seleção sem bloquear eventos

- [x] 1.1 Separar captura, obtenção HTTP e aplicação do detalhe do pet para executar em background, usando sessão/alvo/geração; verificar `tests/unit/test_pet_selection.py` com resposta pendente e troca de seleção.
- [x] 1.2 Disparar histórico e consultas concorrentemente após validar o detalhe, sem buscar acessos/auditoria; verificar com barreiras assíncronas que ambas as leituras começam antes de liberar qualquer resposta e que cada rota é chamada uma vez.
- [x] 1.3 Aplicar o conjunto clínico somente após sucesso completo, priorizando 401/403, e encerrar loading apenas da geração atual; verificar falha parcial, timeout, 429, negação de acesso e respostas atrasadas em `tests/unit/test_clinical_state.py`.
- [x] 1.4 Cobrir seleção A→B, A→B→A, volta à lista, logout e nova sessão durante HTTP com testes determinísticos; verificar ausência de dados, erro ou loading herdados da seleção anterior.
- [x] 1.5 Documentar em `docs/clinical-flow.md` os gatilhos e limites de concorrência; verificar coerência com as rotas efetivamente chamadas nos testes.

## 2. Reutilização e atualização dos dados

- [x] 2.1 Implementar validade de 60 segundos na seleção atual, evento curto de seção e deduplicação de carga; testar relógio controlado antes/depois do prazo e zero novas chamadas ao alternar seções com dados válidos.
- [x] 2.2 Implementar Atualizar e Tentar novamente com descarte das respostas anteriores, sem polling; verificar uma única carga útil após cliques repetidos e recuperação após falha sem renovar validade indevidamente.
- [x] 2.3 Carregar autorizações/auditoria sob demanda com estados independentes, preservando seus controles e conteúdo; testar ausência dessas chamadas na seleção e em Vacinas, sua execução explícita e falha sem apagar histórico válido.
- [x] 2.4 Revalidar reservas após agendamento e acessos/auditoria pertinente após consentimento, invalidando leituras anteriores; testar operação para pet selecionado e para outro pet no modal, sem troca silenciosa de contexto nem repetição de escrita.
- [x] 2.5 Documentar TTL, atualização manual e limites de atualização externa em `docs/clinical-flow.md`; verificar que os testes de sessão, negação e seleção comprovam limpeza do cache sem persistência no navegador.

## 3. Loading e recuperação na interface

- [x] 3.1 Adicionar spinner/skeleton e texto “Carregando dados do pet…” com `role="status"` e `aria-busy` na região correta, distinguindo detalhe e conjunto clínico; verificar no navegador que o loading aparece antes de liberar respostas artificiais lentas.
- [x] 3.2 Separar estados de carregamento, vazio confirmado e falha; disponibilizar Atualizar/Tentar novamente e entradas de autorizações/auditoria; verificar sucesso vazio, erro parcial e nova tentativa no navegador.
- [x] 3.3 Manter menu, troca de pet, saída e acesso a configurações responsivos durante carga e espera por 429; verificar que esses eventos concluem antes de liberar a resposta pendente, inclusive com teclado e viewport móvel.
- [x] 3.4 Registrar o percurso de loading/recuperação e acessibilidade em documentação de verificação da change, sem tokens ou dados clínicos; verificar que os passos reproduzem os cenários da spec.

## 4. Verificação integrada e evidências

- [x] 4.1 Executar as suítes relevantes de seleção, clínica, autenticação, navegação e configurações e `reflex compile --dry` pela `.venv`; registrar comandos, resultados e limitações na change.
- [x] 4.2 Comparar antes/depois com latência HTTP controlada: seleção executa detalhe mais duas leituras clínicas, troca de seção válida gera zero leituras e duas leituras clínicas se sobrepõem; registrar contagens e tempos de loading, navegação e carga completa separadamente.
- [ ] 4.3 Validar o percurso desktop/celular ponta a ponta com backend acessível ao Xano, `/ping` e WebSocket ativos; registrar seleção, navegação, atualização, falha/recuperação e troca rápida de pet, distinguindo testes mockados de verificações reais.
