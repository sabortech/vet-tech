# Design

## Context

As conversas humanas e diretas usam `.vt-chat-bubble` e a classe `.is-user` no `assets/support-chat.css`. O balão enviado usa atualmente `--vt-icon-bg`, uma cor muito próxima da superfície do chat. Em `assets/support-chat.js`, `send()` registra a mensagem localmente, esconde o banner e exibe um recibo; a transição para Visto deve ocorrer somente após resposta válida do bot. `resetConversation()` já é o ponto de entrada para uma conversa nova. O build servido em `.web/public` pode ficar desatualizado em relação a `assets/` até a próxima compilação.

## Goals / Non-Goals

**Goals:** Destacar balões enviados com preenchimento opaco derivado das cores sólidas do tema; mostrar Entregue até uma resposta válida do bot e então mostrar Visto; ocultar e pausar o vídeo após o primeiro envio; restaurar vídeo e estado ao iniciar uma conversa nova.

**Non-Goals:** Alterar mensagens recebidas, regras de atendimento, persistência do chat, payloads ou serviços backend.

## Decisions

- Dar estilo aos balões próprios por meio de `background-color` calculado a partir de cores opacas já disponíveis (`--vt-icon-bg`, superfície e cor de destaque), preservando formas e layout. O cálculo deve continuar opaco nos dois temas.
- Manter um sinalizador efêmero do navegador para indicar que a conversa atual já recebeu uma mensagem do tutor. A função de envio marca esse estado e oculta o banner; `resetConversation()` limpa o estado antes de preparar a saudação da nova conversa.
- A visibilidade do banner será aplicada pelo caminho compartilhado de modo do chat, para que retornar do histórico não o reexiba na conversa atual. Fluxos humanos e histórico continuam ocultando e pausando o vídeo.
- Mensagens do bot mostrarão recibos locais com ícone e rótulo: Entregue enquanto aguardam resposta; somente uma resposta bem-sucedida muda as mensagens pendentes para Visto. Falhas e timeouts não confirmam leitura.
- A URL do script de chat receberá uma versão explícita para evitar reutilização do arquivo anterior pelo cache do navegador.

## Risks / Trade-offs

- Cores muito suaves ainda podem parecer transparentes → validar contraste perceptual nos temas claro/escuro e preservar cores de texto legíveis.
- Mudanças de modo podem reexibir o banner indevidamente → manter a decisão de visibilidade vinculada ao estado efêmero da conversa e testar retorno do histórico e nova conversa.
