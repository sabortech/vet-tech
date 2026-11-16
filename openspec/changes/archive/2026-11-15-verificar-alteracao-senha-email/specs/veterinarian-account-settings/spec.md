# Spec Delta

## MODIFIED Requirements

### Requirement: Troca de senha médica valida credencial atual
O backend SHALL oferecer POST veterinario/password, verificar senha atual contra o campo senha da conta autenticada, exigir nova senha não vazia e confirmação exatamente igual e armazenar nova senha como hash. SHALL preservar caracteres e política existente, sem retornar ou registrar senhas. Após sucesso a interface SHALL limpar credenciais e sessão atual e conduzir ao login com confirmação. O backend SHALL exigir também desafio e código de e-mail válidos, vinculados à conta autenticada e à finalidade de alteração de senha, antes de qualquer escrita. A solicitação de código SHALL validar a senha atual e enviar somente ao e-mail cadastrado, sem aceitar destinatário ou identidade escolhidos pelo cliente. Requisições diretas ao endpoint de troca sem essa confirmação SHALL ser rejeitadas.

#### Scenario: Senha atual errada ou confirmação divergente
- **GIVEN** um veterinário informa senha atual errada ou novos campos inconsistentes
- **WHEN** solicita a troca
- **THEN** a operação é rejeitada sem modificar a senha ou encerrar a sessão por simples erro de validação

#### Scenario: Troca confirmada
- **GIVEN** credenciais atuais, nova confirmação e código de e-mail válidos
- **WHEN** o backend confirma a troca
- **THEN** a sessão local é limpa, a nova senha permite login e a antiga deixa de permitir quando diferente

#### Scenario: Solicitar confirmação por e-mail
- **GIVEN** uma sessão do perfil correto e senha atual válida
- **WHEN** a pessoa solicita o código em Segurança
- **THEN** o código é enviado ao e-mail cadastrado e nenhuma senha é alterada

#### Scenario: Endpoint direto sem confirmação
- **GIVEN** senha atual válida, mas código ausente, inválido ou de outra conta ou finalidade
- **WHEN** o cliente chama diretamente o endpoint de alteração
- **THEN** o backend rejeita sem modificar credenciais

#### Scenario: Confirmação completa
- **GIVEN** senha atual válida, nova senha consistente e código válido da própria conta para alteração
- **WHEN** a pessoa confirma a atualização
- **THEN** o backend altera a senha uma única vez, consome o desafio e a interface encerra a sessão atual
