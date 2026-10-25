# Especificação de apresentação da tela de login

## Purpose

Definir uma apresentação visual responsiva para a tela de login de tutor conforme o protótipo fornecido e a identidade já adotada pela aplicação. A apresentação deve preservar o comportamento atual do login e não sugerir que opções de autenticação ainda não implementadas estejam funcionais.

## Requirements

### Requirement: A tela de login segue a referência visual aprovada
O sistema SHALL apresentar a tela de login existente com a hierarquia e o estilo visual do protótipo aprovado: um cartão dividido com cantos arredondados, uma área clara para o formulário, uma área com imagem de floresta, a marca Vet Tech, mensagem de boas-vindas, campos de credenciais, ação primária, divisor, apresentação de entrada secundária e convite ao cadastro. A imagem exibida no painel direito SHALL também aparecer como fundo da página com efeito de desfoque, mantendo o conteúdo do cartão e a imagem do painel lateral nítidos.

#### Scenario: Renderização do login em desktop
- **WHEN** uma pessoa acessa a rota de login em uma viewport desktop
- **THEN** o sistema exibe formulário e identidade visual no painel claro e a imagem florestal no painel adjacente, com proporções, tipografia, cores, espaçamentos e cantos arredondados correspondentes ao protótipo aprovado
- **AND** a mesma imagem aparece ampliada e desfocada atrás do cartão, sem desfocar seus conteúdos

#### Scenario: Exibição das opções visuais do protótipo
- **WHEN** a tela de login é renderizada
- **THEN** os elementos de lembrar acesso, recuperação de senha e login Google são apresentados conforme o protótipo, sem introduzir novas ações nem afirmar que esses fluxos estão disponíveis

### Requirement: O layout de login permanece utilizável em telas estreitas
O sistema SHALL adaptar a composição de login a viewports estreitas para que os campos de credenciais, ação de envio, mensagens de status e navegação de cadastro existente permaneçam visíveis e utilizáveis.

#### Scenario: Renderização do login em viewport estreita
- **WHEN** uma pessoa acessa a rota de login em uma viewport estreita
- **THEN** o formulário se adapta sem overflow horizontal e o painel decorativo de imagem pode ser ocultado ou reposicionado para preservar o acesso aos controles de login
- **AND** o fundo desfocado não encobre nem prejudica a leitura ou interação com o formulário

### Requirement: As mudanças visuais preservam o contrato de login existente
O sistema SHALL continuar aceitando e-mail e senha na tela existente, usando o login compartilhado que identifica o perfil no backend e preservando mensagens, carregamento, sessão e acesso ao cadastro. A tela SHALL NOT exigir seleção de perfil para autenticar.
 O campo SHALL indicar apenas E-mail.

#### Scenario: Envio dos campos de login
- **WHEN** uma pessoa envia os campos de e-mail e senha
- **THEN** o fluxo compartilhado valida as credenciais e encaminha para a área de tutor ou veterinário conforme a identidade retornada pelo backend

#### Scenario: Exibição da indicação “E-mail ou CPF” do protótipo
- **WHEN** a pessoa acessa o formulário baseado no protótipo com indicação “E-mail ou CPF”
- **THEN** o sistema substitui essa indicação por E-mail e usa validação de e-mail, sem sugerir autenticação por CPF

### Requirement: Limitação temporária do serviço tem feedback seguro no login
Quando o serviço de autenticação responder HTTP 429, o sistema SHALL informar que as solicitações foram limitadas temporariamente e orientar a pessoa a aguardar antes de tentar novamente. SHALL preservar o estado não autenticado e liberar o formulário após o erro, sem repetir automaticamente as credenciais nem exibir o corpo arbitrário retornado pelo serviço.

#### Scenario: Serviço limita as solicitações
- **GIVEN** a pessoa envia e-mail e senha pelo formulário existente
- **WHEN** o serviço responde HTTP 429
- **THEN** a tela informa o limite temporário e orienta aguardar
- **AND** a sessão continua não autenticada e o formulário permite uma tentativa posterior

#### Scenario: Erro contém conteúdo sensível ou não estruturado
- **GIVEN** a resposta HTTP 429 contém JSON arbitrário ou texto não estruturado
- **WHEN** o erro é apresentado à pessoa
- **THEN** o sistema usa uma mensagem segura, sem reproduzir o corpo da resposta
- **AND** não realiza uma nova tentativa automática com as credenciais

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
