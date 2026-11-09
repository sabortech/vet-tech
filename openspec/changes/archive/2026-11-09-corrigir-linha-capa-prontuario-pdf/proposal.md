# Proposal

## Why

A linha horizontal da capa do prontuário exportado atravessa a tartaruga porque é desenhada depois da mascote. A composição deve fazer a linha desaparecer atrás da ilustração, conforme solicitado pelo usuário (RF10).

## What Changes

- Posicionar a linha em camada anterior à tartaruga de canto na capa do PDF.
- Preservar espessura, cor e textos; no refinamento final solicitado, aumentar a tartaruga em 20%, alinhando sua extremidade direita à borda do papel e preservando sua proporção e posição vertical.
- Verificar o resultado em PDF sintético e executar a suíte existente de exportação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `clinical-records`: explicitar a sobreposição da tartaruga à linha divisória na capa exportada.

## Impact

Ajuste restrito a `_cover` em `vet_tech/features/clinical/consultation_pdf_template.py`. Reutiliza ReportLab e os assets locais. Não altera dados sensíveis, autorização do tutor, auditoria (RN01–RN08), endpoints ou notificações automáticas. Evidências devem usar somente dados sintéticos.
