# Proposal

## Why
A aba Horários do veterinário usa um menu isolado e uma agenda pouco informativa. A referência fornecida orienta uma agenda visual com cards de pets, integrada à identidade das outras telas.

## What Changes
- Reutilizar o layout lateral verde, recolhimento e drawer existentes com somente Horários e Consultas, os destinos veterinários implementados.
- Remodelar somente Horários: navegação diária/semanal, seletor de data, resumo e linha do tempo responsiva com cards, foto disponível e status legível.
- Preservar atualização, paginação, início/retomada de atendimento, histórico e logout.
- Ampliar a projeção autenticada da agenda para incluir foto do pet somente com consentimento ativo. Sem duração clínica presumida nem disponibilidade fictícia.

## Capabilities
### New Capabilities
- `veterinarian-schedule-presentation`: apresentação e navegação da agenda veterinária integrada ao sistema.
### Modified Capabilities
Nenhuma.

## Impact
Componentes clínicos, composição de perfil, extensão opcional do menu compartilhado, estado da agenda, CSS isolado e endpoint Xano da agenda. Sem novas dependências ou mudanças no cadastro e no prontuário. Foto/nome/motivo são dados privados: o backend mantém restrição por profissional e consentimento, e as ações de histórico/atendimento mantêm autorização e auditoria existentes (RF03/RF04, RN01–RN08). Nenhuma mudança em notificações automáticas.
