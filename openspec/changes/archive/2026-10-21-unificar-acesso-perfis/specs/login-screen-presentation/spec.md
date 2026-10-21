## MODIFIED Requirements

### Requirement: As mudanças visuais preservam o contrato de login existente
O sistema SHALL continuar aceitando e-mail e senha na tela existente, usando o login compartilhado que identifica o perfil no backend e preservando mensagens, carregamento, sessão e acesso ao cadastro. A tela SHALL NOT exigir seleção de perfil para autenticar.

#### Scenario: Envio dos campos de login
- **WHEN** uma pessoa envia os campos de e-mail e senha
- **THEN** o fluxo compartilhado valida as credenciais e encaminha para a área de tutor ou veterinário conforme a identidade retornada pelo backend

#### Scenario: Exibição da indicação “E-mail ou CPF” do protótipo
- **WHEN** o campo de credenciais é apresentado
- **THEN** a indicação informa E-mail e não sugere autenticação por CPF
