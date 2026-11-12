# Retomada da implementação do chat tutor–veterinário

Contexto atualizado em 11/11/2026. Este documento orienta a próxima sessão.

## Conclusão desta retomada

As três tarefas restantes foram implementadas e verificadas: **20/20 concluídas**.
O workflow foi publicado na versão `b00b335f-f6e9-4f38-ad62-19dd124a9da3`.
Foram alterados somente o assistente do tutor e a normalização da resposta;
as APIs Xano já publicadas não foram republicadas. O ciclo real pelo navegador
passou, com dois veterinários disputando um chamado, retry sem duplicação após
perda de confirmação, mensagens nos dois sentidos, reconexão, retomada,
encerramento e isolamento entre contas. A regressão do visitante também passou.

Consultar `verification.md` da change para as evidências finais e
`docs/n8n-chat.md` para a publicação. A instância atual de teste está na porta
3003. As alterações locais permanecem sem commit/push e a change não foi
arquivada. As seções abaixo preservam o roteiro histórico anterior à conclusão;
não repetir publicação das APIs nem as tarefas já marcadas como concluídas.

## Objetivo e autorização

O usuário autorizou implementar a change `chat-tutor-veterinario-pos-bot`,
incluindo a integração n8n e os testes. O escopo é funcional, sem proposta de
design: após conversar com o bot, o tutor pode confirmar o compartilhamento
do contexto e abrir um chamado para conversar com um veterinário.

Se não for possível alterar o n8n, informar o impedimento ao usuário para que
ele faça a alteração. Não declarar a integração concluída com resposta simulada.

## Estado atual

- A change está em `openspec/changes/chat-tutor-veterinario-pos-bot/`.
  Ler `proposal.md`, `specs/`, `tasks.md` e `verification.md` antes de continuar.
- Existem 17 de 20 tarefas concluídas. Restam 2.4 (workflow publicado),
  4.1 (ciclo completo real) e 4.2 (falhas desse ciclo).
- Backend humano publicado seletivamente no Xano de desenvolvimento:
  perfil `vetech`, workspace `167758`, grupo `vettech-support`, endpoints
  `tutor/chat` e `veterinario/chat`, função `Support/operate` e tabelas
  `support_ticket` e `support_lock`.
- Aplicativo implementa confirmação de pet/consentimento, fila mínima,
  assunção exclusiva, mensagens persistentes e idempotentes, retomada,
  cancelamento, encerramento e isolamento entre participantes.
- O contrato opcional `handoff` já é validado no cliente n8n e no estado
  privado do Reflex. Falta verificar sua emissão pelo workflow real.
- 28 testes unitários, 21 verificações de backend, isolamento clínico,
  testes reais da conversa humana e retenção, regressão real do bot visitante
  e compilação Reflex passaram. O teste da confirmação do encaminhamento
  usa ponte simulada e não comprova o fluxo n8n completo.
- As alterações desta funcionalidade ainda não foram commitadas nem enviadas.
  Conferir `git status` e preservar alterações existentes.

## Conexão MCP: primeiro passo após reiniciar

Servidor cadastrado globalmente no Codex como `n8n-vet-tech`:

```text
https://vet-tech.app.n8n.cloud/mcp-server/http
```

A autenticação OAuth foi concluída: o comando retornou
`Successfully logged in.` após a autorização do usuário. Entretanto, as
ferramentas n8n não apareceram no catálogo da sessão em que foi configurado.
Reiniciar o Codex e retomar esta conversa para carregar a conexão.

1. Descobrir as ferramentas MCP n8n disponíveis e confirmar as permissões
   efetivas. Se necessário, conferir `codex.cmd mcp list` no PowerShell.
2. Identificar o workflow do webhook usado pelo aplicativo e ler sua
   configuração. Não assumir o ID ou substituir um workflow sem inspecioná-lo.
3. Guardar uma cópia privada da configuração antes de editar. Não colocar
   credenciais, tokens, transcrições reais ou a URL OAuth temporária em docs.
4. Se o MCP não carregar, a versão não permitir edição ou faltarem permissões,
   comunicar o erro concreto ao usuário. Não usar o segredo do webhook como
   credencial MCP e não pedir tokens pelo chat.

## Alteração a realizar no n8n

Consultar primeiro [o contrato funcional](chat-veterinario.md) e
[a integração existente](n8n-chat.md). Preservar `ok`, `request_id`,
`conversation_id`, `reply` e `error`, incluindo a correlação dos IDs recebidos.
Quando houver indicação de atendimento humano, acrescentar:

```json
{
  "handoff": {
    "type": "veterinary",
    "reason": "Motivo resumido do encaminhamento"
  }
}
```

- Emitir apenas para `user.authenticated = true` e `user.role = tutor`.
- `reason`: entre 1 e 1000 caracteres, sem segredos; não acrescentar IDs
  de pet, tutor, chamado ou profissional no objeto.
- Sem encaminhamento, omitir `handoff` ou usar `null`; manter a conversa comum.
- O bot somente propõe. A criação ocorre no backend após confirmação explícita
  de pet próprio e consentimento. Não criar chamados diretamente no workflow.
- Não enviar automaticamente mensagens da conversa humana para o bot.
- Validar a alteração e publicar o workflow, se a ferramenta permitir;
  salvar a edição não comprova que o webhook de produção usa a nova versão.

## Verificação a concluir

1. Testar o webhook publicado com conversa comum, encaminhamento para tutor
   autenticado e ausência de encaminhamento para visitante/veterinário.
2. Executar com duas sessões autenticadas o fluxo real:
   navegador → Reflex → n8n → confirmação de pet/consentimento → chamado Xano
   → assunção pelo veterinário → mensagens nos dois sentidos → encerramento.
3. Verificar nesse fluxo falhas de rede, retry sem duplicação, disputa de
   assunção, resposta tardia do bot, retomada e isolamento entre contas.
   Ampliar os testes existentes quando necessário para cobrir o encaminhamento
   real: o teste humano atual prepara contexto pela API.
4. Executar os comandos de regressão documentados em `chat-veterinario.md`,
   a regressão `tests/integration/n8n_bridge_smoke.py`, a compilação Reflex,
   a validação OpenSpec estrita, `node --check assets/support-chat.js` e
   `git diff --check`. Seguir as skills Reflex para compilar/reiniciar.
5. Registrar evidências sem dados sensíveis em `verification.md` e atualizar
   as três tarefas restantes somente após comprovar seus critérios.

Executar testes remotos em sequência: o Xano pode limitar requisições e o
ledger compartilhado não deve ser usado por dois processos simultâneos.
Os comandos e as limitações estão em `chat-veterinario.md`.

## Ambiente e cuidados de continuidade

- A instância de teste foi executada em `http://localhost:3002`; verificar
  se ainda está ativa e reiniciá-la conforme a skill. Não encerrar a instância
  do usuário na porta 3000. Uma pequena alteração final do JavaScript exige
  reconstruir a instância de teste para validar a versão atual dos fontes.
- Fixtures sintéticas: ledger privado em
  `.venv/clinical-smoke/support-chat-20261111`. Os chamados de teste pendentes
  foram encerrados; preservar histórico e eventos. Não excluir tutores/pets
  referenciados com o cleanup clínico genérico.
- `SUPPORT_CHAT_BRIDGE_SECRET` já foi configurado privadamente no Reflex e
  Xano. Não expor valores nem alterar credenciais sem necessidade.
- Chat não libera prontuário e não cria consulta, receita ou diagnóstico.
  A autorização clínica continua independente e aplicada no backend.
- A correção anterior da conexão n8n é outra change, já arquivada e integrada
  pela PR #28, com a issue #24 `Chat-N8N` encerrada. Não reabrir essa entrega
  como se fosse a implementação atual; a issue relacionada ao chat humano é #25.
- Não arquivar esta change enquanto houver tarefas pendentes. Não presumir
  que a autorização de merge da correção anterior vale para publicar esta
  nova funcionalidade no GitHub.
