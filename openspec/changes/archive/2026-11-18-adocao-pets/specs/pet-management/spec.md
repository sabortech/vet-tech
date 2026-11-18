# Spec Delta

## MODIFIED Requirements

### Requirement: Operações de pets exigem autenticação e não permitem edição nesta etapa
O sistema SHALL exigir autenticação de tutor para cadastrar, listar, consultar individualmente ou adotar pets. Consulta individual SHALL verificar propriedade no backend; adoção SHALL ser somente a transferência específica de um pet disponível, conforme a capacidade de adoção. Edição genérica e exclusão dos dados de pets não fazem parte desta etapa.

#### Scenario: Requisição sem autenticação
- **GIVEN** uma pessoa não possui autenticação válida de tutor
- **WHEN** tenta cadastrar, listar, consultar individualmente ou adotar pets
- **THEN** o sistema nega a operação sem criar, transferir ou revelar registros

#### Scenario: Transferência não libera edição genérica
- **GIVEN** um tutor autenticado adotou um pet
- **WHEN** tenta alterar outros campos do pet ou excluir o registro por uma operação não prevista
- **THEN** o backend não oferece essas operações e preserva os dados existentes
