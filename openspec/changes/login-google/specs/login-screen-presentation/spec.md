## MODIFIED Requirements

### Requirement: A tela de login segue a referência visual aprovada
O sistema SHALL apresentar a tela de login existente com a hierarquia e o estilo visual do protótipo aprovado: um cartão dividido com cantos arredondados, uma área clara para o formulário, uma área com imagem de floresta, a marca Vet Tech, mensagem de boas-vindas, campos de credenciais, ação primária, divisor, entrada com Google e convite ao cadastro. A imagem exibida no painel direito SHALL também aparecer como fundo da página com efeito de desfoque, mantendo o conteúdo do cartão e a imagem do painel lateral nítidos.

#### Scenario: Renderização do login em desktop
- **WHEN** uma pessoa acessa a rota de login em uma viewport desktop
- **THEN** o sistema exibe formulário e identidade visual no painel claro e a imagem florestal no painel adjacente, com proporções, tipografia, cores, espaçamentos e cantos arredondados correspondentes ao protótipo aprovado
- **AND** a mesma imagem aparece ampliada e desfocada atrás do cartão, sem desfocar seus conteúdos

#### Scenario: Exibição das opções visuais do protótipo
- **WHEN** a tela de login é renderizada
- **THEN** os elementos de lembrar acesso e recuperação de senha são apresentados conforme o protótipo, sem introduzir novas ações nem afirmar que esses fluxos estão disponíveis
- **AND** a entrada com Google mantém a aparência do protótipo e só é acionável quando o login Google estiver habilitado no ambiente

## ADDED Requirements

### Requirement: Entrada com Google inicia e conclui o fluxo pela tela de login
Quando o login Google estiver habilitado, o sistema SHALL apresentar "Entrar com Google" como botão acessível por teclado e leitor de tela, desabilitado durante envio, que inicia o fluxo sem pedir perfil. O sistema SHALL oferecer uma rota de retorno que usa o mesmo cartão de autenticação (LED de perímetro e sombra verde), mostra carregamento, conclui o login e encaminha para a área do perfil autenticado ou de volta a `/login` com mensagem genérica. Quando desabilitado, o botão SHALL permanecer inerte e não afirmar que o fluxo existe. O login por e-mail e senha SHALL continuar disponível e inalterado.

#### Scenario: Entrada com Google habilitada
- **GIVEN** o login Google habilitado no ambiente
- **WHEN** a pessoa aciona "Entrar com Google" por clique ou teclado e escolhe uma conta Google de uma identidade cadastrada
- **THEN** chega à área do seu perfil sem digitar a senha do Vet Tech, inclusive no primeiro acesso

#### Scenario: Cancelamento ou falha no Google
- **WHEN** a pessoa cancela no Google ou o retorno falha
- **THEN** volta a `/login` com mensagem genérica, sem sessão e com o formulário de e-mail e senha utilizável

#### Scenario: Conta Google sem cadastro
- **WHEN** o retorno informa que não há conta para o e-mail Google
- **THEN** `/login` exibe a orientação de cadastro com acesso ao cadastro existente

#### Scenario: Entrada com Google desabilitada
- **GIVEN** o login Google desabilitado no ambiente
- **WHEN** a tela de login é renderizada
- **THEN** o elemento Google não inicia nenhum fluxo nem requisição

#### Scenario: Retorno em viewport estreita
- **WHEN** a rota de retorno é exibida em celular
- **THEN** o indicador de carregamento e as mensagens ficam visíveis sem overflow horizontal
