# Proposal

## Why

A tela de cadastro usa a imagem do painel ilustrado também como fundo da página, com desfoque. Repetir essa composição no login cria continuidade visual entre os fluxos de autenticação e aproveita o mesmo recurso de imagem já existente.

## What Changes

- Aplicar ao fundo da página de login a imagem exibida no painel direito, com efeito de desfoque semelhante ao cadastro.
- Preservar o formulário, os controles atuais e o painel lateral sem alterar o fluxo de autenticação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `login-screen-presentation`: ampliar a composição visual do login com a mesma imagem desfocada no fundo da página.

## Impact

- Interface Reflex em `vet_tech/components/auth.py`.
- Nenhuma alteração em API, autenticação, dependências ou assets; será reutilizada a imagem já apresentada no painel direito.
