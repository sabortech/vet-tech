# Design

## Context
A regra sidebar-navigation > button.sidebar-item--active usa var(--vt-surface), que fica escura. O texto herda verde escuro do destaque compartilhado, causando baixo contraste. Links não passam por essa regra.

## Goals / Non-Goals
Corrigir visual de seleção de todos os perfis sem alterar ações ou destinos.

## Decisions
Centralizar destaque em .sidebar .sidebar-item.sidebar-item--active, com fundo branco e texto verde escuro. Unificar hover/focus-visible ativos em verde muito claro. Remover regras duplicadas conflitantes e preservar regras de recolhimento/drawer.

## Risks / Trade-offs
Cascata deve funcionar também em botões e links focados → conferir cores computadas e navegação real em tutor/médico nos dois temas.
