# Continuidade do assistente com veterinário

Para retomar a implementação e concluir o workflow n8n, seguir
[o contexto e roteiro de continuidade](retomada-chat-n8n.md).

## Contrato do n8n

A resposta atual preserva `ok`, `request_id`, `conversation_id`, `reply` e `error`.
Acrescentar opcionalmente:

```json
{
  "handoff": {
    "type": "veterinary",
    "reason": "Motivo resumido do encaminhamento"
  }
}
```

`reason` deve ter entre 1 e 1000 caracteres, sem tokens ou segredos. Não incluir
IDs de usuário, pet, profissional ou chamado nesse objeto. Sem encaminhamento,
omitir `handoff` ou devolver `null`. Texto livre em `reply` não cria chamado.
O workflow só deve propor encaminhamento para `user.authenticated = true` e
`user.role = tutor`. O aplicativo revalida identidade, pet e consentimento.

O bot propõe; o tutor confirma o pet e o compartilhamento. A criação efetiva
acontece pelo backend do aplicativo, nunca por um comando livre da IA.

## Operação

Após confirmação, o chamado entra na fila compartilhada. A fila expõe somente
identificador, estado e horários; o motivo, tutor e mensagens só aparecem após
um veterinário assumir. A transação impede dois responsáveis simultâneos.
O responsável é identificado por nome e CRMV/UF. O tutor e esse profissional
podem trocar mensagens, retomar e encerrar; o tutor pode cancelar enquanto aguarda.
Encerrados continuam somente leitura. Um novo atendimento exige nova conversa.

O controle Atendimentos no chat lista chamados próprios e, para veterinários,
a fila. Eventos persistentes alimentam avisos internos sem texto clínico.
Atualização a cada dez segundos enquanto a fila ou chamado estiver aberto;
fechar o painel não encerra o chamado. Conteúdo fechado não é mostrado a outra
identidade, e a participação é revalidada em cada solicitação ao backend.

`SUPPORT_CHAT_BRIDGE_SECRET` deve ter o mesmo valor privado no servidor Reflex
e no ambiente Xano. Ele protege a criação contra histórico forjado diretamente
na API e não é usado como autenticação do tutor: o token e a propriedade também
são obrigatórios. Payload e bridge_key são entradas sensíveis no Xano. Nunca
copiar valores para este documento, frontend ou registros técnicos.

Chat não concede nem revoga acesso ao prontuário; leituras e gravações clínicas
continuam no fluxo de autorização/auditoria existente. Não cria receitas,
diagnósticos, consultas ou agendamentos. Sem anexos, áudio/vídeo ou novo design.

## Verificação de desenvolvimento

```powershell
.venv/Scripts/python.exe -m unittest tests.unit.test_n8n_client tests.unit.test_support_chat_state tests.unit.test_support_client -q
.venv/Scripts/python.exe scripts/support_chat_smoke.py --development --run support-chat-20261111
.venv/Scripts/python.exe scripts/support_chat_access_smoke.py --development --run support-chat-20261111
.venv/Scripts/python.exe tests/integration/veterinary_support_browser.py --development --run support-chat-20261111 --url http://localhost:3002
.venv/Scripts/python.exe tests/integration/support_retention_browser.py --development --run support-chat-20261111 --url http://localhost:3002
.venv/Scripts/python.exe tests/integration/support_handoff_browser.py --url http://localhost:3002
node --test tests/unit/n8n_support_handoff.test.cjs
.venv/Scripts/python.exe tests/integration/n8n_handoff_smoke.py --run support-chat-20261111
.venv/Scripts/python.exe tests/integration/n8n_support_cycle_browser.py --development --run support-chat-20261111 --url http://localhost:3003
.venv/Scripts/reflex.exe compile --dry
```

O smoke remoto usa o perfil Xano `vetech`, workspace de desenvolvimento 167758,
e cria contas/pets exclusivamente sintéticos com ledger privado em
`.venv/clinical-smoke/<run>`. Não reutilizar dados reais nem publicar ledger,
respostas, tokens ou capturas. Os chamados sintéticos e seus eventos são
preservados para auditoria da verificação; não excluir tutores/pets referenciados
por esses chamados pelo cleanup clínico genérico.

Em 11/11/2026, a validação real das APIs confirmou criação idempotente, bloqueio
de pet alheio, consentimento obrigatório, bloqueio de contexto forjado sem
credencial privada, isolamento entre contas, fila mínima, disputa entre dois
veterinários, envio/retry sem duplicação, resposta humana, encerramento,
histórico persistente e rejeição de adulteração de eventos. O código Xano foi
publicado seletivamente, sem importar registros ou excluir tabelas existentes.

Também passaram as verificações reais no navegador de mensagens bidirecionais,
encerramento e retomada após fechamento, recarga e novo login, com isolamento ao
trocar de tutor. O teste de confirmação/cancelamento, avisos e retry da interface
usa ponte simulada e não aciona n8n/Xano; ele valida os controles e não a
publicação do workflow. Execute os testes reais em sequência, usando o mesmo
ledger em apenas um processo por vez para não disputar evidências nem a cota.

O contrato de encaminhamento foi publicado no workflow n8n; a versão ativa e
os testes diretos por perfil estão registrados em `n8n-chat.md`. O teste
`n8n_support_cycle_browser.py` usa o workflow publicado, confirma pet e consentimento
na interface e verifica disputa entre dois veterinários, retry de mensagem com
confirmação descartada, mensagens bidirecionais, retomada e encerramento. Esse
teste não prepara contexto pela API nem simula a resposta do bot. A injeção de
falha descarta somente a confirmação de uma gravação real; o retry passa pelo
Reflex e Xano existentes. Os resultados ficam no ledger privado, sem conteúdo
sensível na evidência pública.
