# Proposal

## Why

Na aba Consultas do veterinário, Ver Histórico anterior aparece também em consultas ainda não finalizadas. O usuário quer manter essa ação somente nos atendimentos concluídos (RF03).

## What Changes

- Usar o rótulo Ver Histórico anterior para descrever corretamente a ação existente.

- Exibir Ver Histórico anterior no cartão de Consultas somente com status explícito `finalizada` e autorização vigente.
- Preservar iniciar/retomar atendimento e os acessos de histórico em Horários e dentro do atendimento.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `veterinarian-schedule-presentation`: restringir a disponibilidade do histórico nos cartões da aba Consultas ao estado finalizado.

## Impact

Ajuste localizado em `consultation_card`, em `vet_tech/components/veterinary_schedule.py`. Sem novos endpoints, requisições, dados clínicos, notificações ou dependências. Autorização e auditoria continuam no backend existente (RN01–RN08). Verificação com cartões sintéticos por status e compilação Reflex.
