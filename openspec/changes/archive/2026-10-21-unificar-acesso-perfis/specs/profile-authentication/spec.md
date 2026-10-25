## Purpose

Autenticar tutor e veterinário pela mesma entrada, identificando o perfil no backend e impedindo confusão de credenciais e permissões entre entidades.

## ADDED Requirements

### Requirement: Um e-mail possui somente um perfil
O sistema SHALL normalizar e-mail com espaços externos removidos e letras minúsculas e garantir unicidade entre tutor e veterinário, inclusive em cadastros concorrentes e pelos endpoints legados. Um e-mail já utilizado SHALL NOT criar segundo perfil. Conflitos preexistentes SHALL bloquear a resolução ambígua sem escolher conta por ordem de busca.

#### Scenario: Cadastro cruzado
- **WHEN** um e-mail de tutor é enviado para cadastro veterinário ou o inverso
- **THEN** o backend rejeita o segundo cadastro sem criar identidade ou vínculos parciais

#### Scenario: Concorrência entre perfis
- **WHEN** cadastros de tutor e veterinário disputam o mesmo e-mail normalizado
- **THEN** no máximo um cadastro conclui e o outro recebe conflito

#### Scenario: Duplicidade preexistente
- **WHEN** o login encontra o mesmo e-mail nos dois perfis
- **THEN** não emite token e retorna falha genérica sem revelar contas

### Requirement: Login compartilhado deriva identidade no backend
O sistema SHALL aceitar e-mail e senha em `/login`, validar a senha da única identidade correspondente e retornar token vinculado à entidade correta com perfil e identificador. O sistema SHALL NOT confiar em perfil enviado pelo cliente, autenticar por CPF ou usar a entidade genérica `user`.

#### Scenario: Tutor ou veterinário válido
- **WHEN** a pessoa informa as credenciais válidas de um dos perfis
- **THEN** recebe sessão desse perfil e é encaminhada à área correspondente

#### Scenario: Credenciais inválidas
- **WHEN** o e-mail não existe ou a senha está incorreta
- **THEN** o sistema nega acesso com mensagem genérica e sem token

### Requirement: Token isola a entidade autenticada
O backend SHALL validar token, entidade e identidade nas operações protegidas. IDs iguais em tabelas diferentes SHALL NOT conferir os mesmos privilégios. Alterar perfil na interface ou no pedido SHALL NOT mudar a entidade autorizada.

#### Scenario: Perfil forjado
- **GIVEN** um token veterinário cujo ID também existe em tutor
- **WHEN** o cliente declara perfil tutor e chama uma operação de pets do tutor
- **THEN** o backend nega a operação sem dados do tutor

#### Scenario: Token de tutor na área veterinária
- **GIVEN** um token de tutor válido
- **WHEN** ele é enviado a uma operação protegida de identidade veterinária
- **THEN** a operação é negada

### Requirement: Sessão limpa dados da identidade anterior
O sistema SHALL limpar perfil, token, pet, dados, formulários e requisições pendentes em logout, expiração reconhecida e nova identidade. Respostas da sessão encerrada SHALL NOT preencher a nova sessão. Falha de login SHALL NOT preservar uma identidade autenticada anterior.

#### Scenario: Troca de perfil com resposta atrasada
- **GIVEN** um tutor está carregando um pet
- **WHEN** encerra a sessão e um veterinário entra antes da resposta
- **THEN** a resposta é descartada e a nova sessão contém somente a identidade veterinária
