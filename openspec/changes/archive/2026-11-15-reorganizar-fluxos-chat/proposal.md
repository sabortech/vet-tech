# Proposal

## Why
O encaminhamento mistura formulário com atendimentos antigos, cabeçalho e LED perdem alinhamento e falhas não oferecem retomada clara. Consultas periódicas desnecessárias aumentam o consumo do Xano além das duas requisições por troca com o bot.

## What Changes
- Organizar cabeçalho, navegação, formulário, lista, estados de atendimento e erro nos dois temas e celular.
- Separar encaminhamento novo de atendimentos anteriores e manter estes acessíveis apenas por ação explícita.
- Preservar operações no retry, suspender consultas em aba oculta e em atendimento encerrado e eliminar listagem ao buscar pets para encaminhamento.

## Capabilities

### New Capabilities
Nenhuma.

### Modified Capabilities
- `interface-preferences`: LED no perímetro externo em todos os estados.
- `assistant-chat-banner`: banner na largura inteira e proporção original somente no assistente, oculto no histórico e no fluxo humano.
- `support-chat`: apresentação dos fluxos, isolamento do encaminhamento e economia de consultas.

## Impact
Assets do chat, mixin Reflex e testes locais sem IA/Xano reais. Conversa e consentimento continuam sensíveis e privados no servidor; a autorização de participação e propriedade permanece no Xano. Não libera prontuário nem modifica notificações automáticas. Não altera o contrato n8n nem promete eliminar as duas requisições por troca do workflow externo.
