# Proposal

## Why
O botão Hoje e o campo nativo de data não acompanham a identidade visual da agenda. O usuário pediu somente Hoje e um ícone de calendário que abre um painel grande e personalizado.

## What Changes
- Substituir o campo de data visível por um ícone de calendário; estilizar Hoje com os tokens do sistema.
- Abrir diálogo amplo com calendário mensal em português, navegação por mês/ano, dias destacados e tartaruga existente decorativa.
- Selecionar um dia fecha o painel e recarrega a agenda existente; cancelar/Escape preserva a data.
- Adicionar luz verde no sentido horário somente nas bordas da janela aberta, com alternativa estática para movimento reduzido.
- Preservar cabeçalho centralizado, permissões e restante das telas.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `veterinarian-schedule-presentation`: calendário mensal em diálogo acessível, acionado somente por ícone ao lado de Hoje.

## Impact
Componentes e CSS da agenda, estado clínico transitório e testes. Sem mudanças em backend, prontuário, auditoria ou notificações; não cria agendamentos nem amplia autorização. Reutiliza asset local da tartaruga sem dependências novas.
