# Proposal

## Why

O tutor consegue ler o prontuário de uma consulta, mas ainda não pode baixar esse registro em PDF. A entrega deve permitir uma cópia legível e fiel à consulta finalizada, com revalidação de propriedade e auditoria de exportação no Xano (RF03, RF08 e incremento de RF10 do projeto).

## What Changes

- Adicionar `Exportar PDF` ao detalhe existente da consulta do tutor, com processamento, bloqueio de clique duplicado e mensagens seguras.
- Gerar uma consulta por documento A4 em memória, com marca VetTech, conteúdo publicado e complementos vinculados ao mesmo `consulta_id`; baixar `vettech-consulta-<id>.pdf` sem sair do detalhe.
- Revalidar sessão, propriedade, pet, consulta e publicação no backend no momento da exportação. Somente status explícito `finalizada` será elegível na V1; registros sem status/legados continuam legíveis, mas não exportáveis.
- Planejar operação Xano autenticada dedicada para leitura autorizada e auditoria `exportar_consulta`, reutilizando funções e tabela de logs existentes. Falha de auditoria impede entrega; retries usam chave idempotente.
- Descartar resultados após troca de consulta/pet, logout ou mudança de sessão, inclusive durante renderização.
- Incluir testes de conteúdo, paginação, segurança, concorrência, download e regressão, mais documentação breve de implantação.

## Capabilities

### New Capabilities

Nenhuma: exportação e controle de acesso estendem capacidades existentes.

### Modified Capabilities

- `clinical-records`: exportação individual da consulta finalizada do próprio tutor, fidelidade dos vínculos clínicos, layout, download e estados da interface.
- `record-access-control`: autorização e auditoria específica, imutável e idempotente da exportação pelo tutor.

## Impact

Planejamento derivado de `VetTech_OpenSpec_Exportacao_Consulta_PDF.md`, especialmente seção 13, conferido no checkout atual. Esta etapa cria somente artefatos OpenSpec, sem implementação ou commit.

A futura aplicação afeta `components/clinical.py::consultation_detail`, o `ClinicalMixin` do State autenticado existente, um serviço de documento em `features/clinical/`, dependência PDF e testes adjacentes. Reutiliza `shared/xano_client.py` e `shared/dates.py`; não cria segundo cliente nem State de autenticação. O design detalha o novo contrato proposto, sem apresentá-lo como endpoint existente/publicado.

Envolve dados sensíveis do prontuário e identificação mínima do pet. Exige `Clinical/assert_owner` no Xano, auditoria antes de liberar dados e ausência de arquivos públicos, logs clínicos ou credenciais nos artefatos. Sem novas tabelas, armazenamento de PDFs ou alteração de domínio; registro de auditoria na tabela existente. Não altera notificações, não envia e-mail/WhatsApp e não introduz assinatura digital. Exportação veterinária, lote e histórico completo ficam fora desta V1.

Publicação remota Xano, capacidade do deploy e aprovação do modelo visual são checkpoints anteriores à liberação funcional; o planejamento não os afirma verificados.
