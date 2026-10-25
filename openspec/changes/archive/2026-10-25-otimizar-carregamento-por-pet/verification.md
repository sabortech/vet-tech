# Verificação da otimização por pet

## Escopo e execução

As verificações usam a `.venv` do projeto com Reflex 0.9.11. O teste de navegador
usa o aplicativo real compilado em produção e um servidor HTTP local com dados
sintéticos, sem substituir eventos ou estado Reflex. Essa execução comprova o
percurso navegador → WebSocket → estado → cliente HTTP → resposta → interface,
mas não substitui a validação autenticada no workspace Xano real.

O arquivo `.env.example` já estava alterado pelo usuário e não foi modificado
pela implementação. Não houve alteração de schema nem publicação Xano.

## Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests/unit
.\.venv\Scripts\reflex.exe compile --dry
git diff --check
```

Os testes de seleção foram adaptados para executar separadamente os eventos
curtos e os eventos de background que eles agendam. Os testes novos em
`tests/unit/test_pet_clinical_loading.py` verificam HTTP fora do lock,
concorrência das duas leituras, deduplicação, validade de 60 segundos com relógio
controlado, falha parcial, 401/403/404, timeout, 429, recuperação, limpeza de
contexto e respostas antigas após A→B, A→B→A, logout, nova sessão ou volta à lista.
Agendamento revalida reservas somente do pet selecionado; consentimento agenda
revalidação auxiliar sem recarregar o histórico.

Resultado final: **145 testes aprovados**. `reflex compile --dry` compilou todas
as páginas com sucesso. `openspec validate otimizar-carregamento-por-pet --strict`
e `git diff --check` também passaram.

O teste de menu existente foi atualizado para o comportamento especificado de
Mudar pet: abrir o seletor limpa o contexto e invalida a carga anterior. Expandir
menu ou abrir/cancelar cadastro continua preservando a seleção.

## Comparação controlada

Foi executado o corpo original de `load_tutor_clinical` extraído via AST de
`git show HEAD:vet_tech/features/clinical/state.py`, removendo apenas o decorator,
com a mesma sessão sintética e o mesmo cliente HTTP mockado da implementação.
Cada chamada recebeu `asyncio.sleep(0.15)`. Nenhuma conta ou resposta clínica real
foi usada.

| Implementação | Leituras clínicas | Tempo medido |
| --- | ---: | ---: |
| Corpo original, quatro leituras sequenciais | 4 | 628 ms |
| Carga nova, histórico e reservas em paralelo | 2 | 165 ms |

Esses tempos medem a lógica clínica com latência artificial; não representam
latência de produção. O detalhe básico é uma leitura adicional na seleção.
Resolver uma raça ausente da lista pode exigir uma consulta de catálogo.
Navegar entre seções com cache válido produz zero leituras adicionais.

## Percurso de navegador reproduzível

1. Iniciar `.\.venv\Scripts\python.exe tests/integration/pet_loading_browser.py --serve`.
2. Em outro processo, definir `$env:XANO_API_BASE_URL = 'http://127.0.0.1:9010'`
   somente para esse processo e iniciar
   `.\.venv\Scripts\reflex.exe run --env prod --single-port --frontend-port 3000`.
3. Executar `.\.venv\Scripts\python.exe tests/integration/pet_loading_browser.py --browser`.
4. Encerrar ambos os processos de teste e reiniciar o Reflex com a origem real
   carregada do `.env` e acesso à rede. Nunca usar as credenciais sintéticas do
   stub contra o workspace remoto.

O script usa Chrome headless e viewports 1366×900 e 390×900. Verifica spinner e
texto acessível antes da resposta, ausência de estado vazio durante loading,
navegação em cache, falha 503 e Tentar novamente, navegação e configurações
durante espera por 429, troca rápida de pet, leitura auxiliar explícita,
ausência de overflow horizontal e logout. As fontes externas são bloqueadas no
teste para que a rede de terceiros não influencie o resultado.

Os dois percursos foram aprovados, sem erros JavaScript. As respostas clínicas
tinham atraso artificial de 2 segundos (3 segundos no cenário de troca rápida).
O teste também usou Enter no botão de seção para verificar navegação por teclado.

| Viewport | Clique → loading visível | Seleção → dados clínicos | Navegação em cache |
| --- | ---: | ---: | ---: |
| 1366×900 | 157 ms | 2612 ms | 23 ms |
| 390×900 | 68 ms | 2574 ms | 74 ms |

Em ambos, a seleção executou uma consulta de detalhe e duas leituras clínicas.
As chamadas iniciais do login (identidade, espécies e lista de pets) foram
contabilizadas separadamente. A troca de seções não acrescentou chamadas; acessos
e auditoria só foram consultados quando o botão correspondente foi acionado.

## Ambiente real e limites

As fixtures antigas em `.venv/clinical-smoke/20261021-publish/ledger.json` estão
marcadas como removidas (`cleaned: true`). Foi solicitada uma conta de teste ao
usuário para validar a navegação autenticada com dois pets no workspace real.
Esse teste permanece separado das evidências sintéticas; nenhuma credencial
de usuário é registrada neste documento.

O stub foi encerrado e o servidor foi restaurado com a origem do `.env`, usando
`.venv`, modo produção e porta única 3000 com rede externa autorizada. Verificações
finais: `/ping` HTTP 200, `/login` HTTP 200 e upgrade WebSocket em `/_event/`
HTTP 101. O frontend aponta para `ws://localhost:3000/_event`.

As consultas remotas sem credenciais chegaram ao Xano: pets retornou HTTP 401 e
consultas sem parâmetros retornou HTTP 400. Isso comprova conectividade, sem
comprovar o fluxo autenticado. A tarefa 4.3 permanece pendente dessa última
verificação; as outras 16 tarefas foram concluídas.

## Encerramento por aceite

Em 25/10/2026, após ser informado da validação remota pendente, o usuário
solicitou concluir e arquivar a change. A implementação é aceita com essa
ressalva. A tarefa 4.3 permanece desmarcada como registro de teste não executado,
sem bloquear o arquivamento autorizado. Não se declara sucesso de autenticação
ou do percurso completo no Xano real com base nos testes sintéticos.
