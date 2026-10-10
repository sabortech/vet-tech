# Spec Delta

## ADDED Requirements

### Requirement: Cadastro usa uma única tela com identidade visual
O sistema SHALL oferecer um único formulário em `/cadastro`, com a identidade visual existente, todos os dados obrigatórios e layout acessível em desktop e celular. Os acessos ao cadastro SHALL direcionar a essa tela.

#### Scenario: Acesso pelo login ou diretamente
- **WHEN** a pessoa abre `/cadastro` ou escolhe criar conta no login
- **THEN** encontra o mesmo formulário com logo, cores, campos obrigatórios e ação Cadastrar

#### Scenario: Tela pequena
- **WHEN** a pessoa usa uma tela de celular
- **THEN** consegue acessar todos os campos, mensagens e botão por rolagem sem corte do formulário

### Requirement: Confirmação de senha impede envio inconsistente
O sistema SHALL exigir confirmação da senha e rejeitar divergências antes de enviar o cadastro à API.

#### Scenario: Senhas diferentes
- **WHEN** senha e confirmação não coincidem
- **THEN** informa a divergência e não chama a API

### Requirement: Tela apresenta o resultado real do cadastro
O sistema SHALL exibir feedback do CPF, erros da API e estado de envio, impedir novo envio durante uma requisição e retornar ao login com confirmação após sucesso sem autenticar automaticamente.

#### Scenario: API rejeita cadastro
- **WHEN** o endpoint rejeita a conta
- **THEN** exibe a mensagem e mantém os campos disponíveis para correção

#### Scenario: Envio concluído
- **WHEN** a API confirma a criação
- **THEN** apresenta o login com confirmação e limpa senha e confirmação

### Requirement: Controles sem integração não simulam funcionalidade
O sistema SHALL identificar o acesso Google como indisponível e não oferecer persistência de informações pessoais sem implementação.

#### Scenario: Opção Google
- **WHEN** a pessoa visualiza as opções de cadastro
- **THEN** encontra Google indisponível e pode usar o cadastro por e-mail
