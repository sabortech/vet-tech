## Context
Cards implementados como botões temáticos herdam estilos de forma e texto que conflitam com a grade. Diálogo deve conter textos sem rolagem horizontal e permitir a tartaruga na borda.

## Goals / Non-Goals
Organizar o painel antes de ampliar o realce visual. Não alterar os destinos nem ações.

## Decisions
Usar botões HTML para os cards, dimensões explícitas no diálogo, conteúdo interno com rolagem vertical e imagem decorativa externa. Grade em duas colunas largas, uma no celular. Realce por seletores semânticos de controles interativos, sem aplicar a superfícies estáticas; cores de status derivadas dos tokens existentes e atributos Radix. Desabilitados e somente leitura não acendem. Foco de teclado conserva contorno.

## Risks / Trade-offs
O halo precisa conviver com sombras de componentes; usar drop-shadow para preservar sombras existentes e token de cor local. Respeitar movimento reduzido e evitar transformações globais.
