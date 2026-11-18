# Spec Delta

## ADDED Requirements

### Requirement: Resumo clínico de adoção não substitui o prontuário completo
O sistema SHALL fornecer para adoção somente os campos clínicos mínimos autorizados: vacina mais recente com nome e datas de aplicação/próxima dose; medicamentos atualmente prescritos com nome, dose, frequência, tipo e período; condições consolidadas não curadas com nome e estado; e exames recentes com tipo, data e estado. SHALL excluir diagnósticos e observações livres, resultados textuais, anexos e rascunhos. O prontuário publicado completo SHALL continuar disponível somente pelas operações autorizadas ao tutor que possui atualmente o pet.

#### Scenario: Resumo clínico do pet disponível
- **GIVEN** o histórico publicado possui registros de vacina, medicamento, condição ou exame
- **WHEN** o backend prepara a visualização de adoção
- **THEN** retorna somente os campos mínimos permitidos e não altera nem publica registros clínicos

#### Scenario: Prontuário contém narrativas ou anexos
- **GIVEN** uma consulta publicada contém diagnóstico, observações, resultado textual ou arquivo
- **WHEN** outro tutor consulta a adoção antes de ser proprietário
- **THEN** esses conteúdos não aparecem no resumo nem podem ser lidos pelo fluxo de adoção

#### Scenario: Pet é adotado
- **GIVEN** o backend transferiu a propriedade para o tutor autenticado
- **WHEN** esse tutor abre o prontuário completo pelas operações existentes
- **THEN** pode consultar o histórico publicado preservado, sujeito à verificação de propriedade no backend
