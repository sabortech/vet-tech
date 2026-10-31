# Verificação da integração

- `.venv/bin/reflex compile --dry`: compilação concluída.
- `node --check assets/support-chat.js`: sintaxe válida.
- `openspec validate integrar-chat-n8n --strict`: válido.
- Suite completa: 167 testes unitários passaram (Node no PATH). A primeira execução sem Node no PATH falhou nos 19 testes clínicos que o exigem; repetida com o executável já instalado, sem alteração desses testes, passou.
- Testes novos cobrem visitante/autenticado, token apenas em header, redação de credenciais conhecidas no corpo, IDs e schema inválidos, ausência de configuração, HTTPS, segredo inválido, timeout total, JSON inválido, status e expiração de sessão, histórico limitado, pergunta atual não duplicada, sessão forjada, duplicação pendente e descarte após fechar/nova conversa/logout.
- Estado privado: token e contexto de mensagens não aparecem em State.dict enviado ao frontend.
- Playwright em localhost:3000 com transporte simulado: passou em desktop e mobile, com envio/retry, conteúdo seguro, histórico, saudação e reset de identidade, resposta atrasada, foco e pose da mascote.
- Smoke real navegador/Reflex/cliente/retorno ao navegador passou, devolvendo erro amigável de configuração. Não houve sucesso de IA: o segredo estava ausente; isso não valida o webhook remoto ou consultas reais ao Xano.
- Backend antigo da porta 8000 foi parado e iniciado em produção com o código novo, mantendo frontend existente em localhost:3000.
- Proteção adicional: formulário não navega antes da hidratação; mensagens aguardam evento chat-ready. Não se envia texto em query string.

## Validação operacional posterior — 31/10/2026

- Revisão para publicação: 167 testes unitários passaram com Node disponível no
  PATH; sintaxe de `mascote.js` e `support-chat.js` válida.

- Recompilada e reiniciada a instância local com `bash scripts/run-local.sh`,
  carregando o `.env` atual e os assets do chat em `http://localhost:3001`.
- Smoke real `n8n_bridge_smoke.py`: ponte navegador → Reflex → n8n → navegador
  OK e resposta de sucesso do workflow **True**, com pergunta genérica de visitante.
- Usuário confirmou o funcionamento do chat após o reinício.
- Regressão `n8n_chat_browser.py` passou novamente em desktop/mobile, incluindo
  UUIDs, resposta, erro/retry, texto seguro, histórico, sessão, descarte de
  respostas atrasadas, foco e pose da mascote.
- A validação anterior com erro de configuração é um registro histórico;
  o smoke posterior confirma resposta real. Nenhum segredo foi incluído no Git.

## Pendências de operação externa (consultas clínicas)

1. Configuração local e reinício concluídos; manter o segredo fora do repositório.
2. Confirmar no n8n a versão que aceita o token e consulta Xano; não foi publicada nenhuma alteração remota por esta implementação.
3. Corrigir retorno conhecido de consulta Xano 401: responder HTTP 401, ok false, error.code SESSION_INVALID. HTTP 200/ok true contendo só texto de expiração não pode ser interpretado com segurança como sessão inválida.
4. Após esses passos, executar smoke real e confirmar uma consulta com conta de teste autorizada; não imprimir respostas clínicas nem tokens.
