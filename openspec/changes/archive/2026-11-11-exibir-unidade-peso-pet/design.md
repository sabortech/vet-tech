## Context
O atendimento já acrescenta Kg; Dashboard e resumo clínico projetam apenas números. O perfil mostra o campo bruto e o formulário não explicita unidade.

## Goals / Non-Goals
Padronizar exibição em Kg, incluindo zero e decimais já retornados. Não converter valores nem alterar o contrato inteiro do cadastro/backend.

## Decisions
Compartilhar a formatação entre projeções clínicas e Dashboard. Acrescentar Kg ao campo bruto do perfil somente para valor presente. Remover o sufixo separado do atendimento para evitar duplicação. Documentar Kg como convenção do peso cadastrado, substituindo orientações antigas de não inferir unidade.

## Risks / Trade-offs
Não há campo separado para unidade. A mudança adota a convenção Kg já utilizada pelo atendimento; não faz conversões nem migração.
