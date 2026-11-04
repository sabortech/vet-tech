# Design

## Context
Ver proposal.md. O processo ativo foi iniciado com `reflex run` em modo dev; o worker Python morreu e o Vite continuou servindo a tela. `.web/env.json` aponta eventos para 8000.

## Goals / Non-Goals
Restaurar a instância solicitada na porta 3000 usando o launcher existente. Não alterar contratos, contas ou o backend Xano.

## Decisions
Usar `scripts/run-local.sh`, que carrega `.env`, em modo prod com `--single-port`; mudar o fallback de VET_TECH_PORT de 3001 para 3000. Manter override explícito. Reiniciar somente o processo confirmado deste projeto. Não editar arquivos gerados em `.web`.

## Risks / Trade-offs
- Reinício interrompe sessões locais → informar o usuário e verificar nova conexão.
- Senha válida não disponível → validar transporte e rejeição real de credenciais fictícias; informar o limite da verificação.
