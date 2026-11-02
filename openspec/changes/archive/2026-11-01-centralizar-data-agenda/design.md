# Design

## Context
O flex anterior centralizava a data no espaço disponível ao lado dos controles.

## Goals / Non-Goals
Centralizar o cabeçalho mantendo eventos e componentes atuais.

## Decisions
Usar grid com colunas laterais simétricas e navegação na coluna central.
Abaixo de 900 px disponíveis no conteúdo, colocar os controles na linha seguinte
para preservar o centro e evitar sobreposição, independentemente da sidebar.

## Risks / Trade-offs
Controles podem ocupar uma linha adicional em telas intermediárias; verificar
geometria nas larguras 1440, 1280, 1180, 1024, 768 e 390 px.
