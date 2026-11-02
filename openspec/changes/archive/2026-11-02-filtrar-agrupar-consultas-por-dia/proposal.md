# Proposal

## Why

Os filtros de Consultas já existem na interface, mas o endpoint publicado ainda aceita apenas dia e página. A lista contínua dificulta distinguir os dias; o usuário confirmou que Próximas deve abranger hoje e os quatro dias seguintes, com rótulos Hoje/Amanhã.

## What Changes

- Ativar os filtros no backend: Hoje somente no dia atual; Próximas de hoje até hoje + 4 dias; Concluídas somente finalizadas; Canceladas somente canceladas.
- Manter Pendentes para consultas agendadas/em atendimento, inclusive atrasadas, e excluir finalizadas/canceladas das abas ativas.
- Agrupar a lista de cada aba por dia do agendamento, em ordem cronológica, com divisórias Hoje — DD/MM/AAAA, Amanhã — DD/MM/AAAA e apenas a data nos demais dias.
- Preservar busca por nome, filtro de estado, paginação de 25 registros, totais, fotos, resumo e ações existentes.
- Publicar e verificar o contrato Xano correspondente, sem migração ou alteração de consultas existentes.
- Popular cinco novas consultas agendadas de teste para o pet Jessy: uma por dia de hoje até hoje + 4 dias, no mesmo intervalo do filtro. Mantê-las para conferência e exclusão posterior pelo usuário, com identificação de teste e controle dos IDs para evitar duplicação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `veterinarian-schedule-presentation`: filtros temporais e por estado operacionais e agrupamento diário da lista de Consultas.

## Impact

`features/clinical/state.py`, `components/veterinary_schedule.py`, estilos de Consultas e `xano/api/clinical/agenda_GET.xs`; testes e documentação clínica. Backend continua limitando consultas ao profissional e protegendo nome/foto/motivo por consentimento ativo. A leitura explícita do histórico mantém auditoria existente. A população manual adicionará somente cinco consultas de teste para Jessy, sem modificar consultas ou dados clínicos anteriores. Esses cinco registros permanecerão para exclusão posterior pelo usuário; os dados sintéticos descartáveis da verificação automatizada continuam separados e serão removidos. Não criar ou reativar consentimento automaticamente. Sem novas notificações, operação de cancelamento, mudanças na tela Horários ou migrações. A change anterior `redesenhar-consultas-medico` já descreve a base das abas, mas não a janela de cinco dias nem divisórias; esta change complementa essa base sem reescrever seus artefatos.
