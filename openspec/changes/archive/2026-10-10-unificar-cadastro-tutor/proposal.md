# Proposal

## Why

O cadastro funcional e a tela com identidade visual estão separados. A pessoa deve criar sua conta em uma única tela com o design existente e integração real com o Xano.

## What Changes

- Tornar `/cadastro` o único formulário de criação de conta, com logo, mascote e cores existentes.
- Incluir endereço obrigatório, confirmação de senha, CPF com feedback e mensagens de envio e erro.
- Encaminhar os acessos ao cadastro para essa rota e retornar ao login após sucesso.
- Identificar Google como indisponível e retirar lembrar informações e aceite sem documentos ou registro efetivo; não persistir dados pessoais no navegador.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `tutor-registration`: cadastro unificado com design responsivo, confirmação de senha e navegação consistente.

## Impact

Afeta páginas e componentes de autenticação, estado Reflex e testes. Reutiliza o endpoint e as validações Xano, sem alteração no banco. CPF, endereço e senha permanecem dados pessoais; não serão gravados em logs ou armazenamento local. Cadastro público não concede autorização para prontuários, nem modifica auditoria ou notificações.
