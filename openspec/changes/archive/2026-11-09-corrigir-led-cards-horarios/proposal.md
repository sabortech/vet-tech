# Proposal

## Why

Os cartões da aba Horários possuem borda fixa e LED circular na foto, mas não apresentam segmento luminoso circulando pelo perímetro do cartão. O usuário quer o contorno animado nas cores dos estados clínicos (RF03).

## What Changes

- Acrescentar LED de perímetro no cartão da agenda, reutilizando o componente e a animação existentes.
- Usar vermelho para `agendada`, amarelo para `em_atendimento` e verde para `finalizada`.
- Acompanhar as dimensões do cartão e desacelerar com movimento reduzido, sem bloquear ações.
- Preservar os indicadores de foto, permissões e os dados existentes, sem novas requisições.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `veterinarian-schedule-presentation`: incluir LED animado no contorno completo dos cartões de Horários.

## Impact

Alteração visual em `schedule_card` de `vet_tech/components/veterinary_schedule.py` e CSS escopado em `assets/vet_tech.css`. Sem mudanças em dados, autorização, auditoria, endpoints ou notificações (RN01–RN08). Verificação por status, tema, tamanho de tela e movimento reduzido com cartões sintéticos.
