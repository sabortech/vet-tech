## 1. Implementação
- [x] 1.1 Mover seletores para painel inicial e apresentar resumo nominal na confirmação.
- [x] 1.2 Validar seleção atual e preservar troca de pet, bloqueios e vínculo por consulta.
- [x] 1.3 Verificar seleção, isolamento de respostas e payload por pet/médico; compilar Reflex.

Verificação: 3 testes do painel (incluindo dois pets com médicos distintos), 7 testes do calendário e regressões de resposta fora de ordem e reenvio idempotente passaram. Compilação Reflex e validação estrita OpenSpec passaram. Sem alteração de backend.
