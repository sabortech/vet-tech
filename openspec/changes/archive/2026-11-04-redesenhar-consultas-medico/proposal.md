# Proposal

## Why
Consultas precisa seguir o protótipo fornecido, com leitura rápida dos pacientes e resumo contextual, corrigindo informações clínicas inconsistentes.

## What Changes
- Lista horizontal de consultas, busca, abas de pendentes/hoje/próximas/concluídas/canceladas e filtro de estado.
- Busca com contorno pill e filtro por estado com ícone de ajustes.
- Seleção explícita de paciente com resumo autorizado, peso, última vacina, última consulta e alergias registradas no histórico de doenças.
- Ausência de dados será indicada; alergias não serão inferidas de peso nem de ausência de registro.
- Formulário Atendimento e seus painéis seguem a paleta do status, com LED horário/halo no perímetro completo do painel.
- Cards de Horários reutilizam a mesma paleta por estado, inclusive ações e LED da foto.
- Botões, ícones, badge, bordas, foco, avatar sem foto e superfícies dos cards/resumo seguem a paleta do status, com contraste nos dois temas.
- LED no perímetro dos cards de Consultas e do resumo do paciente selecionado: verde concluída, vermelho agendada e amarelo em atendimento, circulação horária com halo móvel.
- Detalhe decorativo com babyturtle.png; preservar sidebar médica e assistente flutuante.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `veterinarian-schedule-presentation`: apresentação de Consultas, filtros e resumo do paciente.

## Impact
Reflex, CSS e contrato aditivo de agenda em XanoScript. Dados sensíveis continuam sujeitos a consentimento e auditoria existentes no endpoint de histórico. Sem mudanças nas regras de gravação, notificações ou permissões do tutor. Verificação com dados sintéticos, testes de estado/contrato e compilação.
