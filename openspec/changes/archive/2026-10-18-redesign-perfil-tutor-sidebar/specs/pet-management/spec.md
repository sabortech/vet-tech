# Spec Delta

## MODIFIED Requirements

### Requirement: Tutor lista somente os próprios pets
O sistema SHALL retornar ao tutor autenticado somente pets cujo vínculo de propriedade aponta para seu próprio registro em `tutor`. O filtro de proprietário SHALL ser derivado da sessão autenticada e não de um identificador fornecido pelo cliente. Para cada pet, a resposta SHALL incluir a foto já associada em formato consumível para exibição quando houver imagem, sem alterar os demais nomes de campos existentes.

#### Scenario: Tutor possui pets cadastrados
- **WHEN** o tutor autenticado solicita sua lista de pets
- **THEN** o sistema retorna todos e somente os pets vinculados a esse tutor
- **AND** inclui a foto de cada pet quando houver imagem associada, sem alterar os demais campos da resposta

#### Scenario: Tutor ainda não possui pets
- **WHEN** o tutor autenticado solicita sua lista e não há pets vinculados a ele
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Tentativa de consultar pets de outro tutor
- **WHEN** o cliente tenta alterar ou fornecer o identificador usado para filtrar a lista
- **THEN** o sistema continua retornando somente pets do tutor autenticado
- **AND** não expõe imagens associadas a pets de outros tutores

#### Scenario: Pet não possui foto
- **WHEN** o tutor autenticado solicita a lista e um pet não possui imagem associada
- **THEN** o sistema mantém o pet na lista sem fabricar uma imagem
