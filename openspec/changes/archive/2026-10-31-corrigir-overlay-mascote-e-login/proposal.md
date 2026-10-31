# Proposal

## Why

A reserva inferior da mascote comprime as páginas e desloca o login. Além disso,
duas instâncias locais de desenvolvimento servem frontend sem backend acessível:
o navegador tenta WebSocket na porta 8000 e a conta não consegue entrar.

## What Changes

- Remover faixa/scrollport e usar overlay global sem espaço no fluxo das páginas.
- Restaurar altura e centralização do login e preservar proporção/animação da mascote.
- Fornecer inicialização local que carrega .env e executa frontend/backend na mesma porta.
- Reiniciar somente instâncias deste projeto e validar login real com a conta indicada,
  sem gravar senha/tokens ou alterar credenciais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `floating-mascot`: presença global sem reservar área nem deslocar conteúdo.

## Impact

CSS/componente global, login, launcher local, documentação e verificações.
O Xano já aceitou a conta e confirmou a identidade (HTTP 200); não mudar contrato
de autenticação ou autorização. Credenciais permanecem somente na execução de QA.
Nenhuma alteração de dados clínicos, notificações, perfis ou auditoria.
