# Proposal

## Why

A foto no card de Horários deixa uma faixa interna visível entre a imagem e a moldura circular. O enquadramento deve preencher essa área e preservar o LED que circula na borda.

## What Changes

- Preencher a área interna do círculo com a foto centralizada, sem distorção e com recorte proporcional.
- Preservar tamanho externo, estrutura, ações e estados do card.
- Manter o LED e seu halo circulando na borda, com a cor do status e desaceleração em movimento reduzido.
- Corrigir também a folga do retrato no histórico anterior, conforme solicitação adicional, mantendo a largura da moldura e tornando o recorte perfeitamente circular.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `veterinarian-schedule-presentation`: definir preenchimento integral da foto circular em Horários, preservando borda animada e interações.

## Impact

Alteração visual localizada em `assets/vet_tech.css`, nos seletores de `.vet-schedule-avatar-frame` e `.history-profile-portrait`. Reutiliza `schedule_card`, `consultation_avatar` e `perimeter_led` sem alterar sua estrutura ou o avatar compartilhado em outras telas. Verificação visual em navegador e regressão dos estados existentes.

Relaciona-se à apresentação da agenda (RF06) e preserva as regras de autorização RN01–RN08. Não altera APIs, dados sensíveis, leituras de prontuário, auditoria ou notificações; o bloqueio de acesso revogado continua vigente no backend.
