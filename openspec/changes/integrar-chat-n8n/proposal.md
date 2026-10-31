## Why
O chat já existe mas responde localmente. Conectar ao workflow n8n informado pelo usuário para perguntas livres e consultas Xano autorizadas.
## What Changes
- Transporte servidor-servidor com segredo e token Xano privados, timeout de 60 s e validação estrita das respostas.
- Evento Reflex de background para integrar o painel existente, mantendo interação e histórico visual.
- Contexto e identidade montados no backend; nova conversa limpa e respostas antigas descartadas.
- Configuração documentada, testes sem produção e erros amigáveis.
## Capabilities
### New Capabilities
- `n8n-chat-integration`: transporte, contrato, isolamento e segurança da integração.
### Modified Capabilities
Nenhuma spec principal adicional: o painel está descrito na change abrir-chat-mascote ainda não sincronizada.
## Impact
RF02–RF05: respostas podem conter dados de saúde dos pets, apenas sob autorização do Xano (RN01–RN08) e auditoria já implementada. Sem novas escritas clínicas nem notificações. O token é enviado ao n8n somente por HTTPS; histórico corrente minimizado para 20 mensagens/20 mil caracteres. Exige configuração do segredo e publicação do workflow remoto correto; não publicar automaticamente.
