# Spec Delta

## ADDED Requirements

### Requirement: Tartaruga encobre a linha divisória da capa do PDF
A capa do prontuário exportado SHALL apresentar a linha divisória horizontal atrás da tartaruga do canto inferior direito. O trecho sobreposto às partes opacas da mascote SHALL ficar encoberto, preservando a composição, os textos e as dimensões atuais do documento (RF10).

#### Scenario: Linha encontra a mascote
- **WHEN** uma consulta elegível é exportada e sua capa é visualizada
- **THEN** a linha permanece visível à esquerda da tartaruga e desaparece atrás de sua silhueta, sem atravessar a ilustração

#### Scenario: Conteúdo do prontuário preservado
- **WHEN** o documento é gerado com dados sintéticos de consulta e textos extensos
- **THEN** identificação, narrativas, acentos e páginas internas continuam íntegros e legíveis

#### Scenario: Mascote reposicionada para a esquerda
- **WHEN** a capa é gerada após o refinamento solicitado pelo usuário
- **THEN** a extremidade direita da tartaruga fica alinhada à borda direita do papel, mantendo posição vertical e sobreposição à linha divisória

#### Scenario: Mascote ampliada na capa
- **WHEN** a capa é gerada após o pedido de aumento
- **THEN** a tartaruga aparece 20% maior, com proporções preservadas, junto à borda direita e sem encobrir os textos da capa
