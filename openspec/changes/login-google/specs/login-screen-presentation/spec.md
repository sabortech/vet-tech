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

#### Scenario: Entrada com Google de conta já vinculada
- **GIVEN** o login Google habilitado e a conta Google já vinculada
- **WHEN** a pessoa aciona "Entrar com Google" por clique ou teclado e escolhe a conta
- **THEN** chega à área do seu perfil sem etapa de senha

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
- **THEN** o indicador de carregamento, a etapa de senha e as mensagens ficam visíveis sem overflow horizontal

### Requirement: Primeiro acesso com Google mostra a confirmação de senha
Quando o backend pedir confirmação no primeiro login Google, a rota de retorno SHALL exibir uma etapa que explica que a senha do Vet Tech é pedida uma única vez para vincular a conta Google, mostra o e-mail Google em modo somente leitura e oferece apenas o campo de senha, a ação "Confirmar e entrar" (desabilitada durante envio) e a opção de cancelar e voltar ao login. A etapa SHALL NOT oferecer campo de e-mail editável nem seletor de perfil.

#### Scenario: Confirmação com senha correta
- **GIVEN** a etapa de confirmação exibida
- **WHEN** a pessoa informa a senha correta e confirma
- **THEN** chega à área do seu perfil, e os próximos logins com essa conta Google não exibem a etapa

#### Scenario: Confirmação com senha incorreta
- **WHEN** a pessoa informa uma senha incorreta
- **THEN** a etapa continua visível com o erro seguro do login, o campo de senha é limpo e é possível tentar de novo

#### Scenario: Confirmação expirada ou esgotada
- **WHEN** a confirmação expira ou as tentativas se esgotam
- **THEN** a pessoa volta a `/login` com a orientação de entrar com Google novamente, sem sessão

#### Scenario: Cancelar a confirmação
- **WHEN** a pessoa cancela na etapa de senha
- **THEN** volta a `/login`, a confirmação pendente é descartada da aba e nenhum vínculo é criado
