## Why
As telas clínicas sem pet selecionado só oferecem ir à lista. O tutor precisa de um convite explícito para iniciar o caminho de agendamento escolhendo pet existente ou cadastrando um novo.

## What Changes
- Acrescentar “Gostaria de agendar uma consulta?” abaixo do botão existente no estado vazio compartilhado.
- Abrir diálogo ilustrado com tartaruga e dois cards lado a lado: escolher em Mudar pet ou cadastrar em Meus Pets.
- Reutilizar destinos existentes e tornar o painel responsivo e acessível nos dois temas.

## Capabilities
### Modified Capabilities
- `application-navigation`: orientação para agendamento nas seções sem pet.

## Impact
Componente compartilhado e CSS. Sem leituras extras, alterações de autorização, auditoria ou notificações. Nenhum dado clínico adicional é exposto; o painel só encaminha às páginas existentes.
