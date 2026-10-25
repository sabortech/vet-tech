## Why
O login válido espera consultas auxiliares antes de atualizar a tela e não publica o indicador de envio. RF01 exige feedback coerente e sessão independente da disponibilidade de catálogos.

## What Changes
- Publicar carregamento antes de autenticar e impedir envio duplicado.
- Mostrar perfil autenticado antes das leituras auxiliares, preservando mensagens e limpeza de dados da sessão anterior.
- Corrigir indicação do campo para E-mail, único identificador aceito.

## Capabilities
### Modified Capabilities
- `login-screen-presentation`: feedback imediato e carregamento progressivo.

## Impact
Estado de autenticação, formulário e testes. Sem alteração de credenciais, Xano, autorização, prontuário, auditoria ou notificações. Leituras de pets continuam usando token do tutor (RN05); nenhum dado sensível será registrado.
