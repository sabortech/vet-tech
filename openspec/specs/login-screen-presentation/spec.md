# Especificação de apresentação da tela de login

## Purpose

Definir uma apresentação visual responsiva para a tela de login de tutor conforme o protótipo fornecido e a identidade já adotada pela aplicação. A apresentação deve preservar o comportamento atual do login e não sugerir que opções de autenticação ainda não implementadas estejam funcionais.

## Requirements

### Requirement: A tela de login segue a referência visual aprovada
O sistema SHALL apresentar a tela de login existente com a hierarquia e o estilo visual do protótipo aprovado: um cartão dividido com cantos arredondados, uma área clara para o formulário, uma área com imagem de floresta, a marca Vet Tech, mensagem de boas-vindas, campos de credenciais, ação primária, divisor, apresentação de entrada secundária e convite ao cadastro.

#### Scenario: Renderização do login em desktop
- **WHEN** uma pessoa acessa a rota de login em uma viewport desktop
- **THEN** o sistema exibe formulário e identidade visual no painel claro e a imagem florestal no painel adjacente, com proporções, tipografia, cores, espaçamentos e cantos arredondados correspondentes ao protótipo aprovado

#### Scenario: Exibição das opções visuais do protótipo
- **WHEN** a tela de login é renderizada
- **THEN** os elementos de lembrar acesso, recuperação de senha e login Google são apresentados conforme o protótipo, sem introduzir novas ações nem afirmar que esses fluxos estão disponíveis

### Requirement: O layout de login permanece utilizável em telas estreitas
O sistema SHALL adaptar a composição de login a viewports estreitas para que os campos de credenciais, ação de envio, mensagens de status e navegação de cadastro existente permaneçam visíveis e utilizáveis.

#### Scenario: Renderização do login em viewport estreita
- **WHEN** uma pessoa acessa a rota de login em uma viewport estreita
- **THEN** o formulário se adapta sem overflow horizontal e o painel decorativo de imagem pode ser ocultado ou reposicionado para preservar o acesso aos controles de login

### Requirement: As mudanças visuais preservam o contrato de login existente
O sistema SHALL continuar aceitando e-mail e senha na tela existente, usando o login compartilhado que identifica o perfil no backend e preservando mensagens, carregamento, sessão e acesso ao cadastro. A tela SHALL NOT exigir seleção de perfil para autenticar.

#### Scenario: Envio dos campos de login
- **WHEN** uma pessoa envia os campos de e-mail e senha
- **THEN** o fluxo compartilhado valida as credenciais e encaminha para a área de tutor ou veterinário conforme a identidade retornada pelo backend

#### Scenario: Exibição da indicação “E-mail ou CPF” do protótipo
- **WHEN** o campo de credenciais é apresentado
- **THEN** a indicação informa E-mail e não sugere autenticação por CPF
