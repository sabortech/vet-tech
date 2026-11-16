# Spec Delta

## MODIFIED Requirements

### Requirement: Troca de senha valida a credencial atual no backend
O sistema SHALL exigir senha atual, nova senha e confirmação; a nova senha SHALL ser não vazia e coincidir exatamente com a confirmação. SHALL preservar os caracteres das senhas, sem remover espaços silenciosamente, e permitir mostrar ou ocultar cada campo. O backend SHALL validar a senha atual contra a conta de tutor autenticada e armazenar a nova senha como hash, sem retornar ou registrar credenciais. Não SHALL introduzir regra de complexidade ou tamanho mínimo diferente da política atual do tutor nesta change. O backend SHALL exigir também desafio e código de e-mail válidos, vinculados à conta autenticada e à finalidade de alteração de senha, antes de qualquer escrita. A solicitação de código SHALL validar a senha atual e enviar somente ao e-mail cadastrado, sem aceitar destinatário ou identidade escolhidos pelo cliente. Requisições diretas ao endpoint de troca sem essa confirmação SHALL ser rejeitadas.

#### Scenario: Senha atual inválida
- **GIVEN** um tutor autenticado informa senha atual incorreta
- **WHEN** solicita a troca
- **THEN** o backend rejeita a operação e a senha existente permanece válida

#### Scenario: Nova senha ausente ou confirmação divergente
- **WHEN** a nova senha está vazia ou diverge da confirmação
- **THEN** o sistema apresenta erro antes da chamada e o backend também rejeita uma requisição direta inconsistente sem escrita

#### Scenario: Troca confirmada encerra a sessão atual
- **GIVEN** a senha atual é válida, os novos campos são consistentes e o código de e-mail é válido
- **WHEN** o backend confirma a atualização
- **THEN** a interface limpa campos de senha, dados de conta e sessão atual e redireciona para `/login` com confirmação
- **AND** um novo login aceita a nova senha e rejeita a anterior quando elas são diferentes

#### Scenario: Campos de senha deixam de ser usados
- **WHEN** o tutor sai da seção Segurança ou encerra a sessão
- **THEN** os campos de senha e seus estados de visibilidade são limpos, sem persistência em armazenamento do navegador

#### Scenario: Solicitar confirmação por e-mail
- **GIVEN** uma sessão do perfil correto e senha atual válida
- **WHEN** a pessoa solicita o código em Segurança
- **THEN** o código é enviado ao e-mail cadastrado e nenhuma senha é alterada

#### Scenario: Endpoint direto sem confirmação
- **GIVEN** senha atual válida, mas código ausente, inválido ou de outra conta ou finalidade
- **WHEN** o cliente chama diretamente o endpoint de alteração
- **THEN** o backend rejeita sem modificar credenciais

#### Scenario: Confirmação completa
- **GIVEN** senha atual válida, nova senha consistente e código válido da própria conta para alteração
- **WHEN** a pessoa confirma a atualização
- **THEN** o backend altera a senha uma única vez, consome o desafio e a interface encerra a sessão atual
