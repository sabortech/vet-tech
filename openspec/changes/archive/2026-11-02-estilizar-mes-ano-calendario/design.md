# Design

## Context
O wrapper de select usa alinhamento ao item selecionado e aparência padrão. O diálogo já gerencia foco e contém eventos de mês/ano existentes.

## Goals / Non-Goals
Melhorar somente os dois seletores; preservar eventos, dias, efeitos e restante das telas.

## Decisions
Compor Select.Root/Trigger/Content/Item Radix existentes, com chevron-down explícito. Content usa position=popper, side=bottom e avoidCollisions=false para impedir inversão vertical. Limitar altura pelo espaço disponível abaixo e rolar itens. Prop Radix avoidCollisions é enviada via custom_attrs, pois a versão Python não declara esse campo. Classes exclusivas vet-date-select e tokens de tema isolam o estilo.

## Risks / Trade-offs
Em telas baixas a lista fica menor; manter rolagem interna. Validar a geometria em desktop/celular e navegação com teclado.
