# Design

## Context
No Chromium real a variável de ângulo do calendário avança, mas o gradiente extenso da borda torna o movimento discreto. O chat nativo em dialog usa cores hexadecimais claras fixas, fora das classes Radix.

## Goals / Non-Goals
Garantir movimento visível na borda da janela e tema consistente no chat. Preservar mensagens, foco, sessão, transporte e endpoints.

## Decisions
Substituir o gradiente por SVG retangular arredondado, normalizado por pathLength=100, com um segmento luminoso animado por stroke-dashoffset de 0 a -100. Isso percorre o perímetro no sentido horário sem depender de @property. SVG decorativo não recebe eventos e acompanha o tamanho da janela. Respeitar movimento reduzido com destaque estático. Somente o pop-up recebe esse efeito.

Aplicar tokens globais var(--vt-*) a todos os elementos do chat. Como o diálogo permanece no mesmo documento, herda os tokens de html[data-vt-theme] inclusive no top layer nativo; não precisa de tema paralelo, listeners ou armazenamento próprio. Texto do cabeçalho e envio usa token de contraste apropriado ao verde; demais textos, superfícies e estados têm tokens de tema.

## Risks / Trade-offs
SVG não deve encobrir controles → pointer-events:none e apenas stroke na borda. Chat exige contraste em toda a árvore → verificar saudação, mensagens do usuário, histórico, formulário e ações nos dois temas, incluindo mudança com painel aberto e páginas públicas/autenticadas.
