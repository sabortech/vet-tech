## MODIFIED Requirements

### Requirement: E-mail de tutor é único
O sistema SHALL normalizar o e-mail e impedir a criação de uma conta de tutor com e-mail já cadastrado em tutor ou veterinário, inclusive em solicitações concorrentes.

#### Scenario: E-mail válido e ainda não cadastrado
- **WHEN** uma pessoa informa um e-mail válido e não utilizado
- **THEN** o sistema permite prosseguir com o cadastro usando o e-mail normalizado

#### Scenario: E-mail já cadastrado
- **WHEN** uma pessoa informa um e-mail que já pertence a uma conta de qualquer dos dois perfis
- **THEN** o sistema rejeita o cadastro sem criar uma segunda conta com esse e-mail

### Requirement: Cadastro usa uma única tela com identidade visual
O sistema SHALL oferecer `/cadastro` compartilhado entre tutor e veterinário, com seleção do perfil a cadastrar, campos adequados, identidade visual existente e layout acessível em desktop e celular. Os acessos ao cadastro SHALL direcionar a essa tela; selecionar perfil SHALL NOT conceder privilégios de sessão.

#### Scenario: Acesso pelo login ou diretamente
- **WHEN** a pessoa abre `/cadastro` ou escolhe criar conta no login
- **THEN** encontra a mesma tela com logo, cores, escolha de perfil e ação Cadastrar

#### Scenario: Tela pequena
- **WHEN** a pessoa usa uma tela de celular
- **THEN** consegue acessar todos os campos, mensagens e botão por rolagem sem corte do formulário

#### Scenario: Seleção do perfil tutor
- **WHEN** a pessoa escolhe cadastrar tutor
- **THEN** são solicitados os dados obrigatórios atuais de tutor, mantendo validação de CPF e confirmação de senha
