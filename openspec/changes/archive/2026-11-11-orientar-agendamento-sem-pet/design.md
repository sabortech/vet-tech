## Context
Prontuário, Vacinas, Medicamentos, Doenças e Consultas compartilham pet_selection_empty_state. Mudar pet usa show_pet_picker e /?selecionar=pet; Meus Pets em / inclui cadastro.

## Goals / Non-Goals
Oferecer o caminho de preparação do agendamento sem duplicar cadastro ou agenda.

## Decisions
Diálogo Reflex local ao componente compartilhado, sem novo estado de negócio. Usar tartaruga WebP existente, tokens de tema, cards inteiros clicáveis e grade de duas colunas no desktop, uma em telas estreitas. Reutilizar show_pet_picker e redirecionamento para /. Fechar por botão, Escape e clique externo com comportamento do diálogo existente.

## Risks / Trade-offs
A ação orienta o tutor para escolher ou cadastrar o pet; não confirma nem abre automaticamente uma consulta antes dessa escolha.
