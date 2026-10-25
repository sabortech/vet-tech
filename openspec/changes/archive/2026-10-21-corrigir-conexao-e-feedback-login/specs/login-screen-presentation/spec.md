# Spec Delta

## ADDED Requirements

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
