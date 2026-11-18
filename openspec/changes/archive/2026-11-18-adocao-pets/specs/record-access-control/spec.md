# Spec Delta

## ADDED Requirements

### Requirement: Leitura pré-adoção é limitada à divulgação autorizada
O backend SHALL exigir identidade de tutor autenticada e disponibilidade ativa do pet, que representa a autorização de divulgação confirmada pelo tutor atual, para devolver o resumo mínimo de adoção. O pet SHALL deixar de ser consultável por esse fluxo assim que a disponibilidade for removida ou a adoção for concluída. A lista SHALL NOT aceitar identificador de tutor como prova de autorização; leituras completas SHALL continuar exigindo as verificações de propriedade existentes.

#### Scenario: Tutor consulta resumo autorizado
- **GIVEN** o tutor autenticado solicita um pet com divulgação autorizada e disponibilidade ativa
- **WHEN** o backend processa a leitura de adoção
- **THEN** retorna somente o resumo permitido, sem revelar o tutor atual ou liberar o prontuário completo

#### Scenario: Tutor tenta consultar pet não disponível
- **GIVEN** o pet não está disponível, a autorização foi retirada ou a adoção já ocorreu
- **WHEN** um tutor tenta consultar seu resumo por identificador
- **THEN** o backend nega a leitura sem revelar dados clínicos nem confirmar dados do proprietário

#### Scenario: Adoção revoga autorizações clínicas anteriores
- **GIVEN** o pet possui autorizações veterinárias ativas antes da adoção
- **WHEN** a transferência de propriedade é concluída
- **THEN** essas autorizações deixam de permitir novas operações veterinárias e o novo tutor pode conceder permissões conforme o fluxo existente
