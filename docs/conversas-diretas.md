# Conversas diretas

No chat, o veterinário usa **Falar com tutor** para pesquisar qualquer tutor cadastrado por nome ou identificador e confirmar **Conversar**. O seletor mostra somente nome e ID. Uma conversa privada por par é criada ou retomada. Ambos os perfis encontram seus contatos em **Conversas**; o tutor também usa **Falar com veterinário** para pesquisar profissionais por nome ou ID e iniciar uma conversa simples. Os dois seletores usam a tartaruga espreitando e LED verde.

Não há pet, fila, assunção, encerramento clínico ou acesso ao prontuário nesse fluxo. Atendimentos mantém sua navegação independente. Mensagens reutilizam emojis, nomes, recibos Entregue/Visto e edição/exclusão próprias por 10 minutos do envio original; o texto removido fica apenas na auditoria privada.

## Backend

`direct_conversation` guarda par único, participantes, mensagens e eventos privados. Endpoints POST `tutor/conversas` e `veterinario/conversas` no grupo `vettech-support` autenticam por perfil e passam a identidade do token para `Direct/operate`. A participação é revalidada no backend antes de qualquer leitura ou alteração. Veterinários pesquisam `tutors`; tutores pesquisam `veterinarians`. Ambos executam `start` selecionando o perfil oposto; o próprio participante sempre vem do token. Ambos podem listar seus pares, ler, enviar e alterar suas próprias mensagens.

Payload operacional: `action`; `page`/`search` na busca; `tutor_id` ao iniciar pelo veterinário ou `veterinario_id` ao iniciar pelo tutor; `thread_id` ao ler/enviar; `operation_id` UUID nas mutações; `message_id` e `expected_revision` ao editar/apagar; `read_through` e `read_revision` ao reconhecer leitura. Identidade enviada pelo navegador não autoriza operações. A resposta expõe `tutors`, `threads` ou `thread`, nunca eventos privados.

Busca e lista têm 20 resultados por página e atualizam por ação explícita, sem requisição por tecla. Só a conversa aberta consulta a cada 20 segundos com foco; painéis fechados/ocultos e modais suspendem a consulta. Recibos são agrupados com a sincronização existente. Mensagens diretas não passam por n8n e não geram par pergunta/resposta do assistente.

## Verificação

- `node --test tests/unit/direct_messages.test.cjs`
- `.venv/bin/python -m unittest tests.unit.test_direct_chat`
- `.venv/bin/python tests/integration/direct_chat_browser.py --chromium <caminho>`
- `.venv/bin/reflex compile --dry`

Publicação seletiva inclui somente tabela, função e dois endpoints novos; não importar registros ou ambiente nem publicar a função Support/operate junto desta mudança.
