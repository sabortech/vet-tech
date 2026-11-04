## Context
O wrapper global já publica vettech:mascote-click. O protótipo define identidade e estados; o usuário pediu camada escura sobre a página.
## Goals / Non-Goals
Entregar interação visual e orientações locais. Integração de IA e leitura de prontuário não fazem parte desta etapa.
## Decisions
Usar dialog nativo modal em controlador local, com backdrop, foco contido e restauração à mascote. Reutilizar wrapper Reflex para carregar assets. Histórico apenas em memória: fechar/minimizar arquivam a conversa se houver mensagem do usuário; cada abertura começa limpa; recarregar descarta. Mobile em tela cheia; desktop 380x600 limitado pela altura disponível, acima da mascote. Mascote visível abaixo da camada translúcida. Conteúdo textual usa textContent; sem HTML de entrada do usuário.
## Risks / Trade-offs
[Confusão com dados reais] → informar suporte local e não apresentar vacina fictícia. [Viewport baixa] → painel encolhe e mensagens rolam.
## Migration Plan
Compilar e reiniciar a instância. Reversão remove assets e chamada do controlador, preservando evento público.

## Pose durante conversa
Enquanto o dialog estiver aberto, o controlador publica `vettech:chat-state` e a mascote mantém a pose hover de braços em V com glow estático aceso, independente de foco ou ponteiro. O rastreamento fica pausado. Ao fechar por qualquer controle ou Esc/backdrop, o estado é removido e hover/foco seguem as regras existentes. Reduced-motion mantém luz e pose estáticas.

## Avatar fornecido
Usar a imagem de perfil enviada pelo usuário em `assets/mascote/chat-avatar.png`, no cabeçalho e nos balões do assistente, centralizada e com recorte circular. Preservar o arquivo original e a mascote flutuante.

## Recorte do avatar
O bitmap fornecido inclui margem e moldura próprias. Aplicar zoom por clip-path circular e object-fit com escala no conteúdo para preencher a moldura visual, sem modificar o arquivo original.

## Reinício e histórico por sessão
Wrapper global publica somente nome e chave pública perfil/identidade autenticados através de atributos DOM; não publica token. Controlador observa mudanças, cancela resposta pendente, elimina conversas e atualiza a saudação. Visitantes recebem orientação geral. Histórico em seção interna com retorno à conversa atual, somente leitura. Cada fechamento arquiva uma conversa com interação; abertura inicia outra. Limite de 20 conversas em memória por aba, descartando as mais antigas; sem persistência ou API nova.

## Ícones dos atalhos
Substituir patinha incompleta por quatro almofadas e base com sinal de cadastro (+). Usar seringa com corpo, êmbolo e agulha separados. Padronizar ícones de atalhos em 19 px, traços arredondados e alinhamento central; manter calendário e balão para consulta e clínica.
