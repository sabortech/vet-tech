# Proposal

## Why

O tutor ainda usa um calendário simplificado no agendamento e um seletor nativo no nascimento do pet, enquanto a área médica já possui um painel visual completo. Reutilizar esse painel uniformiza a experiência e facilita escolher mês e ano sem perder as regras de cada fluxo.

## What Changes

- Usar o painel compartilhado na primeira etapa de Agendar consulta, com seleção de mês/ano, LED, mensagem contextual, dia e horário.
- Usar o mesmo painel no nascimento do pet, com datas futuras indisponíveis, opção de limpar e confirmação em formato brasileiro.
- Adaptar a apresentação compartilhada para dias indisponíveis e operações ocupadas, preservando os consumidores médicos.
- Preservar seleção do pet, horário de 08h–17h, etapa de motivo/profissional, validações e autorização no backend.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `appointment-management`: apresentação do calendário do agendamento do tutor.
- `pet-management`: seleção de nascimento pelo painel compartilhado.

## Impact

Alterações nos componentes existentes de calendário, clínica e pets e em seus estados, com CSS restrito aos fluxos do tutor. Não alterar contratos Xano, dependências ou regras de autorização/auditoria. As datas são dados do pet e do atendimento, mantidos na sessão autenticada e no payload ISO existente. Não criar consultas extras à API ao navegar no calendário nem alterar notificações.
