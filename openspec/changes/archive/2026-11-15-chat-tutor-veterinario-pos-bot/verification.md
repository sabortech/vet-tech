# Verificação em 11/11/2026

## Implementado e verificado

- Grupo `vettech-support`, endpoints autenticados `tutor/chat` e
  `veterinario/chat`, função `Support/operate` e tabelas `support_ticket` e
  `support_lock` publicados seletivamente no workspace de desenvolvimento
  167758. Não houve exclusão nem importação de registros existentes.
- Credencial exclusiva Reflex–Xano configurada privadamente, com entradas
  sensíveis no Xano e valor mantido fora do repositório.
- 28 testes unitários de contrato n8n, estado e cliente humano aprovados.
- Compilação Reflex de produção aprovada na instância de teste, porta 3002.
- 21 verificações reais de backend aprovadas: criação/retry, confirmação
  concorrente, corrida cancelamento/assunção, propriedade, consentimento,
  credencial de criação, isolamento, fila mínima, responsável exclusivo,
  mensagens/retry, reutilização indevida de operação, resposta veterinária,
  encerramento, bloqueio pós-encerramento, persistência e integridade dos eventos.
- Verificação clínica real com fixtures: assumir sem consentimento não libera
  prontuário; consentimento ativo libera leitura auditada; revogação volta a
  bloquear leitura, mantendo a conversa entre os participantes.
- Fixtures e resultados detalhados somente no ledger privado
  `.venv/clinical-smoke/support-chat-20261111`; sem tokens ou conteúdo real aqui.

## Verificação da interface

O teste reproduzível `tests/integration/veterinary_support_browser.py` prepara
contexto sintético pela API e usa duas sessões autenticadas reais. Ele verifica
a parte humana; não comprova o encaminhamento publicado pelo n8n.

Esse teste passou com assunção, mensagens bidirecionais, encerramento e bloqueio
de novos envios após encerrado. `support_retention_browser.py` passou para
fechamento, recarga, logout/login, histórico somente leitura e troca para tutor
sem acesso. `support_handoff_browser.py` passou com ponte simulada: exige escolha
de pet/consentimento, permite desistir antes de criar chamado, preserva o UUID no
retry, não duplica a mensagem, mantém um aviso por evento e retorna ao bot.

A primeira execução identificou espaço insuficiente para clicar em todos os
chamados. A lista passou a ocupar a área rolável da conversa; banner/chips do bot
ficam ocultos durante a operação humana. A confirmação e o chat usam os controles
existentes, sem novo projeto visual.

Execuções simultâneas dos testes atingiram a cota temporária do Xano e disputaram
o mesmo arquivo privado de evidência. As suítes passaram a ser executadas em
sequência; a interface consulta o chamado a cada dez segundos e repete somente
leituras após espera em caso de falha. Escritas continuam com retry manual
idempotente. Login de teste pode repetir o clique após a mensagem explícita de
limitação, sem mudar o comportamento de login do aplicativo.

## Publicação n8n verificada

Nesta sessão, o MCP `n8n-vet-tech` respondeu e confirmou permissões de edição e
publicação. O workflow existente foi inspecionado; sua cópia anterior está
somente em `.venv/clinical-smoke/support-chat-20261111/n8n-before-handoff.json`.
As APIs, funções e tabelas Xano já publicadas não foram republicadas.

Foram atualizados somente o assistente do tutor e a normalização da resposta.
A versão `b00b335f-f6e9-4f38-ad62-19dd124a9da3` foi publicada; uma nova leitura
confirmou workflow ativo, versão publicada igual ao rascunho e os dois parâmetros
iguais ao delta salvo em `scripts/n8n_support_handoff.json`. A validação não
introduziu novos avisos; os avisos do modelo e da organização do canvas eram
preexistentes.

O webhook publicado passou nos quatro cenários de
`tests/integration/n8n_handoff_smoke.py`: conversa comum do tutor sem proposta,
encaminhamento do tutor, visitante sem encaminhamento e veterinário sem
encaminhamento, todos com HTTP 200 e IDs correlacionados. Cinco testes Node
validam a normalização real do delta, incluindo identidade não confirmada,
campos inesperados, vazamento de token e expiração da sessão nas ferramentas.

As tarefas foram concluídas; o arquivamento permanece uma ação separada.

## Regressão final

### Ciclo completo publicado

`tests/integration/n8n_support_cycle_browser.py` passou com três sessões
autenticadas reais (tutor e dois veterinários), em produção local isolada na
porta 3003, recompilada conforme a skill `reflex-process-management`:

- Encaminhamento emitido pelo n8n publicado, com pet e consentimento exigidos
  na interface, seguido de criação autenticada pelo Reflex e Xano existentes.
- Reapresentação da resposta real anterior do bot após a criação ignorada pela
  interface; nenhum contexto compartilhado foi substituído.
- Disputa pela interface entre dois veterinários, com um único vencedor e sem
  transcrição exposta ao perdedor.
- Mensagem realmente gravada no Xano, confirmação deliberadamente descartada
  no navegador e retry pelo aplicativo com o mesmo UUID, sem mensagem duplicada.
- Mensagens nos dois sentidos, sem novas chamadas ao bot durante o chat humano.
- Desconexão do navegador, reconexão e recarga, com recuperação do chamado e
  das mensagens persistentes.
- Encerramento pelo responsável, atualização para o tutor e campo de envio
  desabilitado no histórico encerrado.

Resultados sem conteúdo em `n8n-support-cycle-results.json`, no ledger privado.
Os dados são sintéticos. Os testes preservam chamados e eventos para auditoria.

Houve indisponibilidade transitória do Xano durante a confirmação da identidade
após os logins; o aplicativo mostrou falha, sem criar chamado fictício. A
tentativa manual pelo controle existente permitiu concluir a rodada. Uma
asserção do teste foi corrigida para comparar as chamadas ao bot antes/depois
da fase humana, considerando as tentativas manuais anteriores. Não foi
necessário alterar ou republicar o backend para concluir o ciclo.

O smoke real `n8n_bridge_smoke.py`, como visitante, passou com sucesso verdadeiro
do workflow. A compilação Reflex e os 28 testes unitários passaram após as
alterações. Validação OpenSpec estrita, sintaxe JavaScript e `git diff --check`
passaram. A inspeção dos arquivos alterados não encontrou os segredos privados.

As tarefas 2.4, 4.1 e 4.2 foram concluídas nesta sessão: 20/20 tarefas verificadas.
Além do ciclo real acima, `support_retention_browser.py` passou com o novo chamado
encerrado: fechamento, recarga, novo login, histórico somente leitura e ausência
de acesso após trocar para outro tutor. `n8n_bridge_smoke.py` passou contra a
instância atual na porta 3003, com sucesso verdadeiro do workflow para visitante.

Passaram 28 testes unitários Python, cinco testes Node da normalização publicada,
compilação Reflex, validação OpenSpec estrita, sintaxe JavaScript e
`git diff --check`. As evidências anteriores de autorização clínica e backend
continuam válidas; suas APIs não foram alteradas. Não houve commit, push,
arquivamento da change ou publicação no GitHub.

Ao finalizar, dois chamados sintéticos de tentativas interrompidas foram
encerrados pelo tutor das fixtures, usando somente os IDs do ledger privado.
Nenhum chamado real, mensagem, evento, tutor ou pet foi excluído.
