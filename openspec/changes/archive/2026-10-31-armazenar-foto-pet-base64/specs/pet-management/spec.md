## ADDED Requirements

### Requirement: Foto do pet é armazenada como texto base64
O sistema SHALL aceitar no cadastro de pet uma foto opcional enviada como texto no formato data URI (`data:<content-type>;base64,<conteúdo>`) e SHALL persisti-la sem transformação na coluna de texto `foto` do pet. As leituras de pet que retornam a foto SHALL devolver esse mesmo texto, aplicando os mesmos filtros de propriedade já exigidos para o pet.

#### Scenario: Cadastro com foto em base64
- **GIVEN** um tutor autenticado
- **WHEN** envia o cadastro de um pet válido com `foto` em data URI base64
- **THEN** o sistema cria o pet associado ao tutor autenticado com o texto recebido na coluna `foto`

#### Scenario: Cadastro sem foto
- **GIVEN** um tutor autenticado
- **WHEN** envia o cadastro de um pet válido sem o campo `foto`
- **THEN** o sistema cria o pet com `foto` vazia e sem fabricar uma imagem

#### Scenario: Leitura da foto de pet de outro tutor
- **GIVEN** um tutor autenticado que não é proprietário de um pet com foto
- **WHEN** solicita a lista ou o detalhe de pets
- **THEN** o sistema não retorna o texto da foto desse pet
