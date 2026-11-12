## Why
O peso aparece sem unidade no Dashboard e Prontuário. O atendimento já usa Kg e essa convenção deve ficar explícita nas demais exibições.

## What Changes
- Apresentar peso cadastrado com sufixo Kg em todas as exibições do perfil e resumo clínico.
- Identificar Kg no cadastro, preservando valores e formato de armazenamento.
- Manter ausência como “Não informado”, sem unidade solta ou duplicada.

## Capabilities
### Modified Capabilities
- `pet-management`: explicitar unidade do peso cadastrado.
- `tutor-dashboard`: exibir o peso em Kg nos dois escopos.

## Impact
Apresentação Reflex e documentação. Sem alteração de dados, APIs, autorizações, auditoria ou notificações; não acrescenta exposição de prontuário.
