# Chat Turtle e conversas humanas

A Turtle ajuda a usar o Vet Tech. A saudação é local, não gera requisição extra e usa o avatar `optimized/mascote_logo.webp`. O histórico do assistente fica disponível somente durante a sessão.

## Como usar

- **Nova conversa** reinicia o contexto do assistente.
- **Atendimentos** apresenta os chamados: vermelho aguardando, amarelo em andamento e verde encerrado. Somente um veterinário pode assumir cada chamado.
- **Conversas** apresenta conversas privadas, separadas dos atendimentos.
- **Falar com tutor / Falar com veterinário** abre uma busca por nome ou ID e inicia ou retoma a conversa com o contato escolhido.
- O compositor oferece emojis e recibos de leitura. Mensagens próprias podem ser editadas ou apagadas por até 10 minutos; exclusão mantém um marcador visível.

Seletores e cards usam LED e os mesmos estilos nos dois perfis. A tartaruga espreitando acompanha a borda dos seletores. Fotos dos pets e nomes identificam os atendimentos quando disponíveis no cadastro.

## Consumo e privacidade

O backend valida identidade e participação. Busca paginada é enviada explicitamente, sem consulta por tecla. A conversa aberta atualiza a cada 20 segundos com foco; leitura é agrupada e consultas param quando o painel está fechado ou oculto. Conversas humanas não chamam o assistente n8n.

## Verificação e publicação

Testes Python e JavaScript cobrem transporte, permissões, revisão, prazo e recibos. Testes de navegador usam dados simulados; smoke remoto usa somente contas sintéticas. A compilação é verificada com `reflex compile --dry`.

Os novos endpoints de conversas diretas foram publicados seletivamente no Xano. O repositório também contém regras de encerramento da mudança anterior cuja publicação remota está pendente; não publicar o workspace inteiro sem revisar essas pendências em `reorganizar-fluxos-chat/tasks.md`. A identidade Turtle no prompt remoto do n8n ainda depende de publicação; a saudação e o cabeçalho locais já foram atualizados. Merge de código não publica automaticamente Xano/n8n.

Detalhes: [conversas diretas](conversas-diretas.md), [atendimento veterinário](chat-veterinario.md) e [integração n8n](n8n-chat.md).
