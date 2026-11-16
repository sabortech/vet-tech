# Design

## Context
O chat global é JavaScript/CSS e recebe eventos por ponte Reflex privada; Xano é a autoridade de identidade e participação. Ver proposal.md. A seleção de todos os tutores foi autorizada explicitamente. A mudança anterior de chat permanece independente, inclusive sua decisão pendente sobre finalização.

## Goals / Non-Goals
Conversas privadas sem pet, ticket, contexto do bot ou status clínico. Reutilizar compositor, identidade visual, emojis, recibos e regras de alteração próprias de 10 minutos. Não enviar mensagens externas nem conceder prontuário.

## Decisions
- Novo agregado direct_conversation com chave única por par, IDs de tutor/veterinário, mensagens e eventos; transação usa chave prefixada no support_lock já existente. Uma conversa por par é retomada idempotentemente.
- Endpoints autenticados separados por perfil no grupo existente, chamando Direct/operate com identidade do token, nunca enviada pelo cliente.
- Apenas veterinário pesquisa/inicia; lista de tutores exibe só ID/nome e é paginada em 20, com busca enviada explicitamente. Sem carregar contatos/CPF nem request por tecla.
- Listas próprias incluem nome do interlocutor e contagem de mensagens não vistas; nenhuma conversa alheia é devolvida. Tutor não inicia pares arbitrários e só responde a seus próprios contatos iniciados.
- Ponte Reflex existente recebe prefixo direct_ com validação operacional independente, descartando respostas ao trocar sessão/contexto. Cliente privado reutiliza transporte HTTP existente sem credenciais no navegador.
- Adaptar conversa direta ao apresentador comum com kind=direct, sem criar ticket no Xano. Roteador de operações escolhe API correta; ações clínicas ficam ocultas e o tema volta ao verde de conversa simples.
- Polling apenas da conversa aberta, a 20s, suspenso em aba oculta/fechada e modais. Recibos em lote e edição/exclusão mantêm os limites existentes. Listas atualizam por solicitação explícita; sem notificações externas.

## Risks / Trade-offs
- Diretório geral expõe nomes a médicos → autorização explícita, campos mínimos, paginação e validação do perfil no backend.
- Confusão com atendimento → navegação Conversas e Falar com tutor, aviso de conversa simples e nenhum vínculo com pet/fila/prontuário.
- Corrida ao iniciar/enviar → par único, transação e operation_id idempotente; edição usa revisão.
- Agregado cresce → listagem omite transcrição, busca paginada e apenas conversa ativa consultada; manter arquitetura Xano existente.

## Migration Plan
Publicar somente nova tabela/função/endpoints, sem tocar registros ou importar o workspace inteiro. Testar contas sintéticas e isolamento antes de habilitar UI. Atualizar backend Reflex/assets em conjunto. Rollback desabilita entradas da UI e preserva dados novos para auditoria, sem excluir conversas.

## Acabamento visual
O seletor e os cards de conversas usam LED SVG verde existente, ícones por perfil e botões contornados. Cabeçalho do modal permanece fixo e somente o diretório rola. A caixa dos dois perfis usa título com ações compactas na mesma linha. Nenhuma consulta adicional é necessária para os efeitos visuais.

## Início nos dois perfis
Tutor também pesquisa veterinários (somente ID/nome) e inicia conversa privada pelo mesmo par único. Identidade do próprio participante vem do token, nunca do payload; a busca permanece restrita ao perfil oposto. Ambos os seletores reutilizam a imagem local espreitando.webp. Esta decisão substitui a restrição inicial de início exclusivo pelo veterinário.

A tartaruga dos seletores fica centralizada verticalmente na borda esquerda junto ao LED externo, com margem lateral reservada e tamanho adaptado ao celular.

O mascote ampliado tem a borda recortada da imagem alinhada à linha verde do painel. Em telas estreitas o diálogo reserva espaço à esquerda para preservar a imagem inteira.
