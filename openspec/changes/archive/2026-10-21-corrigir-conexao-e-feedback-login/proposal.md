# Proposta

## Why

A instância principal na porta 3000 serviu arquivos gerados pelos testes com
conexão de eventos apontando para a porta 3011, já encerrada. Também faltava a
origem Xano no ambiente do processo original. Posteriormente, HTTP 429 do Xano
foi apresentado como falha genérica, dificultando distinguir limitação temporária
de credenciais recusadas. Esta change reúne retrospectivamente as correções já
executadas e suas evidências, por solicitação de arquivamento do usuário.

## What Changes

- Restaurar a execução em produção na porta única 3000, com a origem Xano
  carregada pelo ambiente local e arquivos de conexão recompilados.
- Apresentar orientação de espera para HTTP 429, sem repetir credenciais
  automaticamente nem expor o corpo arbitrário do erro.
- Verificar comunicação do navegador, tratamento de erros e entrada válida
  de uma conta sintética temporária até o perfil de tutor.
- Consolidar o registro de diagnóstico antes disperso na fundação do backend.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `login-screen-presentation`: explicitar o feedback temporário de limitação
  de solicitações, preservando contrato de autenticação e sessão existentes.

## Impact

- Cliente compartilhado `vet_tech/shared/xano_client.py`, testes do cliente e
  do estado de autenticação; configuração local e execução Reflex.
- Nenhum endpoint, tabela, senha ou regra de autorização Xano alterado.
- `.env` contém somente a origem do backend, permanece ignorado pelo Git e
  não faz parte dos artefatos arquivados.
- RF01 e tratamento seguro dos erros existentes; nenhuma ampliação de acesso,
  alteração de auditoria clínica ou de notificações.
- O teste positivo da fixture não comprova a senha do usuário nem permite
  afirmar que HTTP 429 foi a única causa de sua tentativa específica.
