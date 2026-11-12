## Why

Os cartões de Consultas do tutor usam verde em todos os estados, dificultando distinguir consultas agendadas de atendimentos em andamento. A cor deve acompanhar o status já informado pelo backend.

## What Changes

- Aplicar paleta amarela ao cartão, LED e sombra de consultas `em_atendimento`.
- Aplicar paleta vermelha ao cartão, LED e sombra de consultas `agendada`.
- Preservar integralmente a aparência verde das finalizadas e o comportamento atual dos demais estados.
- Manter textos de status e regras de disponibilidade do botão Ver prontuário.
- Separar data e horário em campos identificados por título e ícone próprio, com espaçamento e quebra responsiva.
- Retornar o nome do veterinário junto às consultas autorizadas e exibi-lo no cartão; apresentar “Nome não informado” na ausência de nome, sem expor o ID como identificação profissional.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `clinical-records`: cores dos cartões da lista do tutor conforme estado da consulta.

## Impact

Alterações locais em `vet_tech/components/clinical.py`, projeção de apresentação em `vet_tech/features/clinical/state.py` e `assets/vet_tech.css`, reutilizando o LED e as paletas existentes. Sem dependências ou leituras adicionais. Não altera dados sensíveis, autorização do tutor, auditoria, notificações ou contratos da API; os controles existentes continuam aplicáveis.
