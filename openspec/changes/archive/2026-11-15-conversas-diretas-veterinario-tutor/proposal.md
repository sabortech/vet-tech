# Proposal

## Why
Hoje o chat humano exige encaminhamento/atendimento. O veterinário precisa contatar um tutor específico para uma conversa simples, e o tutor precisa localizar e responder essas mensagens sem entrar em uma fila clínica.

## What Changes
- Botão Falar com tutor no chat veterinário abre seleção pesquisável de todos os tutores, conforme autorização explícita do usuário.
- Botão Falar com veterinário no tutor abre seleção de profissionais e permite iniciar o mesmo par privado.
- Ambos os seletores exibem a tartaruga espreitando e LED verde.
- Botão Conversas nos dois perfis apresenta somente conversas das quais a pessoa participa.
- Conversa privada persistente por par veterinário/tutor, com envio, emojis, leitura e edição/exclusão próprias em até 10 minutos, reutilizando o compositor existente.
- Conversas simples não são atendimentos: sem pet obrigatório, fila, assunção, encerramento clínico ou compartilhamento de contexto do bot.

## Capabilities
### New Capabilities
- `direct-messaging`: conversas privadas iniciadas por qualquer um dos dois perfis com contato cadastrado do perfil oposto.
### Modified Capabilities
Nenhuma.

## Impact
Novos artefatos Xano de conversa direta e ponte privada no domínio de chat existente. Dados pessoais limitados a nome e identificador no seletor; somente os dois participantes acessam mensagens e recibos. Não libera prontuário, não altera consultas, não expõe CPF/contatos na busca e não envia notificações externas. A pesquisa usa paginação e envio explícito; a conversa ativa reutiliza sincronização em lote para limitar chamadas.
