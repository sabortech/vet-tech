# Design

## Context

O shell compartilhado de autenticação usa atualmente `/optimized/fundo02.webp` no fundo desfocado e no painel direito. O arquivo solicitado já existe em `assets/mascote/turtleandog.jpeg`, dentro da pasta de assets servidos pela aplicação.

## Goals / Non-Goals

**Goals:** Usar a imagem da mascote somente no painel direito e preservar a floresta no fundo desfocado, mantendo os estilos e a composição existentes.

**Non-Goals:** Alterar formulário, responsividade, autenticação ou otimizar/converter outros assets.

## Decisions

- Referenciar o asset JPEG pelo caminho estático `/mascote/turtleandog.jpeg` somente no painel direito. Manter `/optimized/fundo02.webp` no fundo desfocado.
- Manter `cover`, posição central, desfoque e regras responsivas já existentes; somente a origem da imagem muda.

## Risks / Trade-offs

- A composição da mascote pode enquadrar de forma diferente da floresta com `cover` → manter o enquadramento central existente.

## Migration Plan

Não há migração de dados. A alteração pode ser revertida restaurando a referência anterior ao asset otimizado da floresta.
