# Proposal

## Why

O veterinário precisa baixar o prontuário ao concluir o atendimento e posteriormente ao consultá-lo. Tutor e médico devem conferir as informações em um painel com a tartaruga espreitando pela lateral antes de decidir baixar o documento (RF03, RF10).

## What Changes

- Oferecer Exportar PDF após finalizar e ao reabrir uma consulta finalizada no perfil veterinário.
- Unificar todos os pontos de exportação de consulta, incluindo o tutor, em um painel com o próprio PDF rolável, mascote lateral e botão Baixar PDF no rodapé.
- Abrir a prévia sem disparar download; fechamento cancela o fluxo. O PDF mantém o template aprovado.
- Acrescentar leitura autorizada e exportação auditada para o veterinário, mantendo propriedade do tutor e consentimento profissional ativo no backend.
- Preservar contexto, tratamento de falhas, idempotência e ausência de armazenamento público de documentos.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `clinical-records`: painel prévio compartilhado, acessos de exportação do veterinário e confirmação explícita do download.

## Impact

Reflex em `pages/profile.py`, `components/clinical.py`, `components/veterinary_schedule.py` e `features/clinical/state.py`; reutilização do mapeador e renderizador existentes. Backend Xano em `xano/api/clinical/`, reutilizando `Clinical/assert_access`, `Clinical/history` e `Clinical/audit`. CSS e mascote local existentes.

Envolve dados sensíveis do prontuário: leitura para prévia e liberação de exportação exigem autorização e auditoria no backend (RN01–RN08). Nenhum novo canal de envio, notificação automática ou link público. Não amplia o escopo para relatórios avulsos de Vacinas/Medicamentos/Doenças; “qualquer lugar” significa todos os acessos de exportação da consulta. Após o refinamento solicitado pelo usuário, a prévia deve mostrar o próprio PDF em páginas roláveis, com composição semelhante ao seletor de data e tartaruga ao lado. PDF.js será usado somente como visualizador local do PDF gerado, sem substituir Reflex ou ReportLab.
