## ADDED Requirements

### Requirement: Painel de orientação com cards sem transbordamento
O painel SHALL apresentar dois cards retangulares com cantos suaves em telas largas, texto com quebra, sem sobreposição ou rolagem horizontal. A tartaruga SHALL espreitar na borda do LED. Em telas estreitas o conteúdo SHALL permanecer acessível com cards empilhados.

#### Scenario: Painel em desktop ou celular
- **WHEN** o tutor abre a orientação
- **THEN** todos os textos, ações e cards permanecem visíveis sem transbordamento horizontal

### Requirement: Ações interativas têm realce luminoso contextual
Controles selecionáveis habilitados SHALL ganhar sombra luminosa mais forte sob hover ou foco de teclado, usando cor de status/ação quando disponível e verde padrão nos demais casos. Controles desabilitados ou somente leitura SHALL permanecer sem o novo realce.

#### Scenario: Ação com cor de situação
- **WHEN** o usuário aponta ou foca um controle dentro de contexto com cor de status
- **THEN** o halo acompanha a cor temática daquele contexto

#### Scenario: Controle desabilitado
- **WHEN** o ponteiro passa sobre controle desabilitado ou somente leitura
- **THEN** o novo halo não é aplicado
