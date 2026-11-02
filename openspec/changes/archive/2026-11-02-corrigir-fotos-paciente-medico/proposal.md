# Proposal

## Why

As fotos dos pacientes não aparecem de forma consistente na área médica. A documentação registra contratos Xano ainda pendentes de publicação; o resumo ignora a foto do histórico e o atendimento renderiza somente uma patinha.

## What Changes

- Exibir a foto cadastrada em Horários, Consultas, resumo, atendimento e histórico, quando disponível e autorizada.
- Priorizar a foto da resposta clínica atual no resumo e no atendimento, preservando compatibilidade com a agenda autorizada do mesmo pet.
- Verificar os contratos remotos de `veterinario/agenda` e `Clinical/assert_access`, publicar apenas as alterações necessárias e registrar evidências sem dados reais.
- Mostrar patinha somente quando o banco retorna foto nula/vazia. Distinguir foto existente com falha de exibição da ausência de imagem.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `veterinarian-schedule-presentation`: foto consistente do paciente também no resumo e no atendimento, com origem autorizada e isolamento entre pacientes/sessões.

## Impact

Estado clínico e componentes Reflex existentes; contratos Xano de agenda e acesso clínico; testes de estado, projeções e apresentação. Sem migração ou novas dependências da aplicação. Fotos são dados privados: consentimento e auditoria continuam no backend e respostas antigas não podem restaurar imagens. Sem impacto em notificações automáticas. A publicação remota depende de acesso ao Xano; a pendência não deve ser confundida com correção já entregue.
