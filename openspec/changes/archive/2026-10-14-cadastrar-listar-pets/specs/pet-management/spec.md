## Purpose

Permite que tutores autenticados cadastrem pets e consultem a própria lista de animais, preservando o vínculo obrigatório entre cada pet e seu tutor e sem expor dados de outros tutores.

## ADDED Requirements

### Requirement: A identidade autenticada corresponde a um tutor
O sistema SHALL autenticar o tutor usando a entidade `tutor` do modelo de domínio e SHALL disponibilizar o identificador desse tutor às operações protegidas. O fluxo SHALL funcionar sem depender da entidade `user` ou de tabelas externas ao modelo de domínio.

#### Scenario: Tutor autenticado acessa o perfil
- **WHEN** um tutor fornece credenciais válidas
- **THEN** o sistema estabelece uma sessão autenticada vinculada ao registro correspondente em `tutor`

#### Scenario: Credenciais inválidas
- **WHEN** uma pessoa tenta autenticar com credenciais inválidas
- **THEN** o sistema nega a autenticação e não concede acesso às operações do perfil

### Requirement: Tutor cadastra um pet próprio
O sistema SHALL permitir que um tutor autenticado cadastre um pet com nome e espécie. O pet SHALL ser associado exatamente a esse tutor, sem aceitar do cliente um identificador de tutor que permita associar o registro a outra pessoa. O cadastro SHALL aceitar raça opcional para representar animais sem raça definida e os demais dados do pet definidos no modelo de domínio.

#### Scenario: Cadastro válido
- **WHEN** o tutor autenticado envia nome e espécie válidos, com ou sem os demais dados opcionais
- **THEN** o sistema cria o pet associado ao tutor autenticado e confirma o cadastro

#### Scenario: Tentativa de informar outro tutor
- **WHEN** o cliente inclui no pedido um identificador de tutor diferente ou tenta definir manualmente o proprietário
- **THEN** o sistema ignora ou rejeita esse valor e associa o pet exclusivamente ao tutor autenticado

#### Scenario: Dados obrigatórios ausentes ou espécie inexistente
- **WHEN** o pedido não contém nome ou espécie válida
- **THEN** o sistema rejeita o cadastro, informa os campos que precisam de correção e não cria o pet

### Requirement: Raça pertence à espécie selecionada
Quando uma raça for informada, o sistema SHALL confirmar que ela pertence à espécie selecionada. O sistema SHALL permitir raça não informada para representar um pet SRD.

#### Scenario: Raça compatível com espécie
- **WHEN** o tutor cadastra um pet com uma raça pertencente à espécie selecionada
- **THEN** o sistema aceita o vínculo entre pet, raça e espécie

#### Scenario: Raça incompatível com espécie
- **WHEN** o tutor seleciona uma raça pertencente a uma espécie diferente da selecionada
- **THEN** o sistema rejeita o cadastro e não cria um vínculo inconsistente

#### Scenario: Pet sem raça definida
- **WHEN** o tutor cadastra um pet sem informar raça
- **THEN** o sistema aceita o cadastro com raça vazia e mantém a espécie informada

### Requirement: Tutor consulta opções de espécie e raça
O sistema SHALL disponibilizar ao tutor autenticado as espécies existentes e SHALL permitir consultar as raças associadas a uma espécie específica, usando os cadastros de domínio como fonte de verdade. Requisições sem autenticação SHALL ser negadas.

#### Scenario: Carregar espécies
- **WHEN** um tutor autenticado solicita as opções de espécie
- **THEN** o sistema retorna as espécies cadastradas com identificadores utilizáveis no cadastro do pet

#### Scenario: Carregar raças da espécie selecionada
- **WHEN** um tutor autenticado solicita raças para uma espécie existente
- **THEN** o sistema retorna somente raças associadas à espécie informada

#### Scenario: Espécie sem raças cadastradas
- **WHEN** um tutor autenticado solicita raças para uma espécie válida sem raças associadas
- **THEN** o sistema retorna uma lista vazia e o cadastro continua permitindo raça não informada

#### Scenario: Consulta de catálogo sem autenticação
- **WHEN** uma pessoa não autenticada solicita espécies ou raças
- **THEN** o sistema nega a consulta

### Requirement: Tutor lista somente os próprios pets
O sistema SHALL retornar ao tutor autenticado somente pets cujo vínculo de propriedade aponta para seu próprio registro em `tutor`. O filtro de proprietário SHALL ser derivado da sessão autenticada e não de um identificador fornecido pelo cliente.

#### Scenario: Tutor possui pets cadastrados
- **WHEN** o tutor autenticado solicita sua lista de pets
- **THEN** o sistema retorna todos e somente os pets vinculados a esse tutor

#### Scenario: Tutor ainda não possui pets
- **WHEN** o tutor autenticado solicita sua lista e não há pets vinculados a ele
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Tentativa de consultar pets de outro tutor
- **WHEN** o cliente tenta alterar ou fornecer o identificador usado para filtrar a lista
- **THEN** o sistema continua retornando somente os pets do tutor autenticado

### Requirement: Operações de pets exigem autenticação e não permitem edição nesta etapa
O sistema SHALL exigir autenticação de tutor para cadastrar ou listar pets e SHALL disponibilizar somente essas operações no escopo desta capacidade. Edição dos dados de pets não faz parte desta etapa.

#### Scenario: Requisição sem autenticação
- **WHEN** uma pessoa não autenticada tenta cadastrar ou listar pets
- **THEN** o sistema nega a operação sem criar nem revelar registros