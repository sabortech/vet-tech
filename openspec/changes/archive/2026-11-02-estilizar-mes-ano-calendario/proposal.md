# Proposal

## Why
Os seletores de mês e ano têm aparência genérica e podem abrir acima do botão. O usuário pediu controles no estilo do sistema, com chevron para baixo e opções sempre abaixo.

## What Changes
- Personalizar os dois controles com superfícies verdes suaves, ícones e cantos arredondados.
- Renderizar chevron-down e listas sempre abaixo, com rolagem interna e limite de altura.
- Preservar seleção, navegação do calendário, tartaruga e luz da janela.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `veterinarian-schedule-presentation`: apresentação e direção de abertura dos seletores mensais/anuais.

## Impact
Somente componente e CSS do calendário veterinário; sem backend, dados clínicos, permissões, auditoria ou notificações.
