# Design

## Context
Ver proposal.md. A agenda possui seleção ISO de dia, eventos e CSS próprios. Há calendário de reserva separado que proíbe datas passadas; a agenda precisa permitir histórico.

## Goals / Non-Goals
Melhorar somente a seleção de data da agenda. Não alterar calendário de reservas, consultas, contratos ou backend.

## Decisions
Usar diálogo Radix/Reflex existente para foco, Escape e retorno ao acionador. Estado independente de mês visível/open; seleção chama agenda_choose_day e fecha. Navegação de meses não faz requests nem muda o dia ativo. Usar mês/ano selecionáveis, grade de 42 posições com dias vazios desabilitados e destaque separado para hoje e seleção. Meses em português e semana iniciando segunda-feira. Reutilizar /mascote/mascote_idle.png, decorativa, em painel lateral no desktop e faixa compacta no celular. Botões nativos estilizados e CSS com prefixo vet-date; sem bibliotecas novas. Tokens de tema e largura máxima do diálogo, sem interferir no menu nem no calendário do tutor.

## Risks / Trade-offs
Datas inválidas e limites de ano → validar no servidor, limitar navegação a 1–9999 e testar ano bissexto/virada de ano. Fechamento com mudança de sessão → limpar estado transitório no logout. CSS do portal → aplicar tokens diretamente à classe do diálogo.

## Refinamento confirmado
Luz verde somente na borda da janela aberta, nunca nos botões. Usar gradiente
cônico com ângulo CSS animado de 0 a 360 graus, borda transparente e fundos em
camadas; prefer-reduced-motion desativa rotação. Não adicionar overlay sobre
conteúdo ou animação de layout.
