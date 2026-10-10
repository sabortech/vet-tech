# tutor-registration Specification

## Purpose

Permite que uma pessoa crie uma conta de tutor vinculada à identidade usada pelo restante da aplicação, com dados obrigatórios e validações de identidade aplicadas no servidor.

## Requirements

### Requirement: Cadastro coleta os dados obrigatórios do tutor
O sistema SHALL oferecer um cadastro de tutor com nome, CPF, e-mail, telefone, endereço e senha obrigatórios.

#### Scenario: Cadastro com todos os campos válidos
- **WHEN** uma pessoa envia todos os campos obrigatórios com valores válidos
- **THEN** o sistema aceita o pedido de criação da conta de tutor

#### Scenario: Campo obrigatório ausente
- **WHEN** uma pessoa envia o cadastro sem um ou mais campos obrigatórios
- **THEN** o sistema identifica os campos que precisam ser corrigidos e não cria a conta

### Requirement: CPF é validado e único
O sistema SHALL normalizar o CPF para dígitos, validar seu formato e dígitos verificadores, e impedir que um CPF já cadastrado seja usado por outra conta.

#### Scenario: CPF válido e ainda não cadastrado
- **WHEN** uma pessoa informa um CPF com 11 dígitos válidos e sem conta existente
- **THEN** o sistema permite prosseguir com o cadastro usando o CPF normalizado

#### Scenario: CPF válido com pontuação
- **WHEN** uma pessoa informa um CPF válido formatado ou somente com dígitos
- **THEN** o backend remove a pontuação, valida os 11 dígitos e permite prosseguir com o CPF normalizado

#### Scenario: CPF com formato ou dígitos verificadores inválidos
- **WHEN** uma pessoa informa um CPF inválido
- **THEN** o sistema rejeita o cadastro e indica que o CPF precisa ser corrigido

#### Scenario: CPF com caracteres fora do formato aceito
- **WHEN** uma pessoa informa letras ou pontuação fora do formato de CPF
- **THEN** o sistema rejeita o cadastro sem criar uma conta

#### Scenario: CPF já cadastrado
- **WHEN** uma pessoa informa um CPF que já pertence a uma conta
- **THEN** o sistema rejeita o cadastro sem criar uma segunda conta com esse CPF

### Requirement: E-mail de tutor é único
O sistema SHALL normalizar o e-mail e impedir a criação de uma conta com e-mail já cadastrado.

#### Scenario: E-mail válido e ainda não cadastrado
- **WHEN** uma pessoa informa um e-mail válido e não utilizado
- **THEN** o sistema permite prosseguir com o cadastro usando o e-mail normalizado

#### Scenario: E-mail já cadastrado
- **WHEN** uma pessoa informa um e-mail que já pertence a uma conta
- **THEN** o sistema rejeita o cadastro sem criar uma segunda conta com esse e-mail

### Requirement: Cadastro cria somente uma identidade de tutor
O sistema SHALL persistir a nova conta na entidade `tutor`, armazenar a senha de forma segura e não expor senha ou hash na resposta do cadastro.

#### Scenario: Criação de conta de tutor
- **WHEN** uma pessoa envia dados válidos e únicos para cadastro
- **THEN** o sistema cria a conta na entidade `tutor` e não cria uma identidade na entidade genérica `user`

#### Scenario: Credenciais não são expostas
- **WHEN** o sistema responde a uma tentativa de cadastro
- **THEN** a resposta não contém a senha nem seu hash

### Requirement: Cadastro concluído retorna a pessoa ao login
O sistema SHALL confirmar a criação da conta e permitir que o novo tutor siga para o login sem criar automaticamente uma sessão autenticada.

#### Scenario: Cadastro concluído
- **WHEN** a conta de tutor é criada com sucesso
- **THEN** o sistema confirma o resultado, limpa a senha informada e apresenta o formulário de login

#### Scenario: Falha no cadastro
- **WHEN** o endpoint rejeita o cadastro ou fica indisponível
- **THEN** o sistema informa a falha, não simula sucesso e permite corrigir os dados ou tentar novamente

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
