# Proposal

## Why

O painel lateral do login ainda exibe a imagem de floresta, enquanto a identidade visual atual deve destacar a mascote disponível em `assets/mascote/turtleandog.jpeg`. A troca mantém a composição do cartão e aproxima o login da identidade Vet Tech.

## What Changes

- Substituir somente a imagem do painel direito por `turtleandog.jpeg`, mantendo a imagem de floresta no fundo desfocado.
- Preservar o layout responsivo, o formulário e os fluxos de autenticação existentes.

## Capabilities

### New Capabilities

### Modified Capabilities
- `login-screen-presentation`: especificar a mascote no painel lateral, preservando a floresta como fundo desfocado.

## Impact

- Interface: `vet_tech/components/auth.py`.
- Asset estático: `assets/mascote/turtleandog.jpeg`.
- Especificação de apresentação do login e estratégia de verificação visual desktop/mobile. Sem alterações a APIs, autenticação, dados ou dependências.
