## ADDED Requirements

### Requirement: Login publica feedback e sessão progressivamente
O sistema SHALL publicar o estado de carregamento antes de consultar a autenticação, impedir envios duplicados enquanto ocupado e exibir a sessão confirmada antes de carregar dados auxiliares. O campo SHALL indicar E-mail, sem sugerir CPF.

#### Scenario: Autenticação válida com dados auxiliares pendentes
- **WHEN** a API retorna um token válido
- **THEN** o perfil autenticado é exibido com indicação de carregamento antes de consultar espécies e pets
- **AND** dados de uma sessão anterior são removidos

#### Scenario: Envio duplicado
- **GIVEN** o login está em andamento
- **WHEN** outro envio é recebido
- **THEN** nenhuma nova chamada de autenticação é feita

#### Scenario: Falha auxiliar
- **WHEN** uma leitura auxiliar falha após autenticação válida
- **THEN** a sessão é preservada e a mensagem aparece no perfil

#### Scenario: Credenciais rejeitadas
- **WHEN** a autenticação falha
- **THEN** o formulário é liberado, a sessão permanece não autenticada e o erro seguro é exibido

## MODIFIED Requirements

### Requirement: As mudanças visuais preservam o contrato de login existente
O sistema SHALL continuar enviando as credenciais atuais de e-mail e senha pelo fluxo de login existente e preservar seus estados de carregamento, erro, sessão autenticada e navegação de cadastro. O campo de credenciais SHALL indicar apenas E-mail.

#### Scenario: Envio dos campos de login
- **WHEN** uma pessoa envia os campos de e-mail e senha
- **THEN** o evento e o fluxo de autenticação existentes são usados sem alteração do endpoint, interpretação das credenciais ou gerenciamento da sessão

#### Scenario: Exibição da indicação “E-mail ou CPF” do protótipo
- **WHEN** a pessoa acessa o formulário baseado no protótipo com indicação “E-mail ou CPF”
- **THEN** o sistema substitui essa indicação por E-mail e usa validação de e-mail, sem sugerir autenticação por CPF
