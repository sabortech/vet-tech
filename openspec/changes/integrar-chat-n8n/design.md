## Context
O painel é DOM local, acionado por evento global; State guarda token privado e identidade confirmada. O contrato n8n fornecido exige UUIDs, contexto anterior sem pergunta atual e identificação validada no Xano.
## Goals / Non-Goals
Conectar o painel existente sem widget externo. Não publicar o fluxo, corrigir seu código remoto ou armazenar conversas em banco.
## Decisions
- Cliente compartilhado em shared/n8n_client.py: URL HTTPS configurada no servidor, sem redirects, timeout 60 s, sem retries automáticos, validação de IDs/status/schema, sem logs sensíveis. Falha de configuração não impede login no app.
- Mixin em features/support_chat/state.py integrado ao State de autenticação, reaproveitando a sessão existente. Form Reflex oculto recebe apenas ação, mensagem e IDs; background libera lock durante HTTP. Credenciais nunca entram em payload/estado público/eventos do navegador.
- Backend mantém conversa e histórico privados, deriva perfil/nome/token da sessão e controla contexto. Atributo de sessão do navegador é apenas guarda contra corridas, não autorização.
- Browser cria UUID da conversa ao abrir e da mensagem ao enviar; descarta eventos de resposta com IDs ou geração antigos. Fechar/iniciar/alterar sessão invalidam estado do servidor e cliente. UI aguarda até 65 s e oferece retry manual sem duplicar pergunta; backend HTTP é limitado a 60 s.
- Receber resposta via rx.call_script com JSON escapado como argumento de evento. Texto é renderizado por textContent. Respostas retornando segredo/token conhecidos são rejeitadas, erros técnicos nunca atravessam a fronteira.
- SESSION_INVALID com contrato válido expira sessão local; 401/403 fora do contrato é configuração, sem deslogar. Não interpretar texto livre como autorização ou expiração. Bug remoto que retorna sucesso com texto de sessão expirada requer correção no n8n.
## Risks / Trade-offs
[Produção antiga] → documentar necessidade de publicar rascunho e corrigir retorno de 401; testes locais não comprovam publicação.
[Resposta antiga após logout] → comparar geração da sessão, token, conversa e requisição antes de publicar resultado.
[Histórico clínico] → somente conversa corrente, últimos 20 itens/20 mil caracteres; sem persistência no navegador ou logs locais novos.
## Migration Plan
Configurar URL/segredo no .env, compilar e reiniciar backend de produção; manter frontend da porta usada pelo usuário. Sem alteração de schema Xano. Reversão restaura o controlador anterior e remove ponte, preservando login.
