## Context
A API aceitou a conta indicada em 0,92 segundo. O handler aguarda catálogos e pets antes de publicar qualquer atualização.

## Goals / Non-Goals
Publicar feedback e sessão antes das consultas auxiliares; preservar contrato e tratamento seguro de erros. Sem alterar endpoint, política de acesso ou implementar login por CPF.

## Decisions
Usar gerador assíncrono com yield, conforme documentação Reflex, antes da API e depois da sessão. Manter is_busy durante todo o carregamento para bloquear duplicatas; is_loading_pets sinaliza perfil incompleto antes das consultas. Falhas auxiliares não invalidam sessão. Não paralelizar chamadas ao Xano pois há evidência de HTTP 429 nesse ambiente.

## Risks / Trade-offs
As consultas auxiliares continuam dependentes da latência do Xano, mas deixam de bloquear a exibição da sessão autenticada. Conexões HTTP por chamada permanecem como estão para evitar introduzir ciclo de vida compartilhado fora deste ajuste.

## Verification
Testes avançam o gerador para comprovar indicador antes da API, sessão antes dos catálogos, bloqueio de duplicatas, erros sem perda de sessão e limpeza dos dados antigos. Executar suíte unitária e compilação Reflex.
