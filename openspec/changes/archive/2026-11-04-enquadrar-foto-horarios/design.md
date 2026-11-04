# Design

## Context

Ver `proposal.md` para motivação. `schedule_card` compõe uma moldura de 52 × 52 px com padding de 4 px, um wrapper autorizado, `consultation_avatar` e um SVG de LED irmão. O avatar tem regra local de 42 × 42 px. Existem wrappers intermediários, portanto remover apenas o padding não garante preenchimento. O avatar é compartilhado com Consultas e outros painéis.

## Goals / Non-Goals

**Goals:** resolver o dimensionamento de todos os wrappers dentro da moldura e preservar o LED independente.

**Non-Goals:** mudar composição Reflex, eventos, fontes de foto, estado, backend ou estilos globais do avatar compartilhado.

Ampliação solicitada durante a aplicação: o retrato de histórico anterior também possui padding de 6 px e espaço de baseline do wrapper inline, produzindo moldura de 120 × 127 px em desktop. Corrigir com dimensões explícitas de 120 × 120 px (110 × 110 px no celular), sem padding, dimensionando wrapper/avatar a 100% e recortando apenas a imagem com `cover`. Preservar borda, sombra, layout do painel e controles. O histórico não possui LED próprio; o LED existente de Horários permanece preservado.

## Decisions

- Ajustar somente seletores CSS sob `.vet-schedule-avatar-frame`: remover a folga interna e dimensionar o wrapper autorizado, `.consultations-avatar` e `.rt-AvatarRoot` para a área interna disponível, mantendo os 52 px externos e a borda.
- Aplicar recorte circular ao conteúdo da foto e `object-fit: cover` com posição central. Manter overflow do frame compatível com o halo: não cortar o SVG irmão nem seu brilho. Esta separação resolve a ambiguidade entre preencher o círculo e preservar a animação.
- Reutilizar `perimeter_led` e suas regras de cor, halo, direção e movimento reduzido sem reimplementação. Não aplicar regras genéricas a todos os filhos, pois o SVG também é filho da moldura.
- Manter os fallbacks e o cadeado existentes. A alternativa de ampliar o avatar global afetaria telas fora do escopo; reconstruir o card introduziria risco desnecessário aos eventos.

## Risks / Trade-offs

- Recorte proporcional elimina partes periféricas da foto → usar centralização e validar fotos horizontais, verticais e quadradas; não prometer enquadramento inteligente do rosto.
- Wrappers sem altura definida podem manter folgas → conferir dimensões computadas de cada camada em navegador.
- Overflow aplicado no nível errado pode cortar halo → recortar somente a imagem/conteúdo interno e comparar a animação em instantes distintos.
- Seletores compartilhados podem afetar Consultas → restringir todas as regras à moldura de Horários e comparar os avatares das outras telas.
