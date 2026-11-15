# profile-authentication Specification

## Purpose

Autenticar tutor e veterinário pela mesma entrada, identificando o perfil no backend e impedindo confusão de credenciais e permissões entre entidades.

## Requirements

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

### Requirement: Login com Google autentica somente identidades existentes
O sistema SHALL permitir que tutor e veterinário entrem com Google, sem digitar a senha do Vet Tech, conduzindo no backend a troca do código de autorização, a validação das claims do Google (`iss`, `aud`, `exp`, `sub` e `email_verified`) e a emissão do token. O token SHALL ser gerado contra a tabela da identidade resolvida, com o mesmo perfil, claims e validade do login por senha, e a sessão SHALL ser entregue no mesmo formato (`authToken`, `perfil`, `identidade_id`). O fluxo Google SHALL NOT criar tutor, veterinário, registros em `user` ou reservas de e-mail, e SHALL NOT aceitar perfil, e-mail ou identificador enviados pelo cliente.

#### Scenario: Tutor existente entra com Google
- **GIVEN** um tutor cadastrado cujo e-mail é o e-mail verificado de uma conta Google
- **WHEN** ele conclui o login Google
- **THEN** recebe sessão de tutor sem digitar senha e é encaminhado à área do tutor

#### Scenario: Veterinário existente entra com Google
- **GIVEN** um veterinário cadastrado cujo e-mail é o e-mail verificado de uma conta Google
- **WHEN** ele conclui o login Google
- **THEN** recebe sessão de veterinário sem digitar senha e é encaminhado à área veterinária

#### Scenario: Conta Google sem cadastro
- **WHEN** o e-mail Google não corresponde a nenhuma identidade
- **THEN** o backend não emite token nem cria conta
- **AND** a pessoa é orientada a usar o cadastro ou o login por e-mail e senha

#### Scenario: E-mail Google não verificado
- **WHEN** o Google informa `email_verified` falso ou ausente para um `sub` ainda não vinculado
- **THEN** o backend nega o acesso com mensagem genérica e não cria vínculo

#### Scenario: E-mail em dois perfis
- **WHEN** o e-mail Google corresponde a tutor e veterinário ao mesmo tempo ou a reserva de e-mail diverge da identidade
- **THEN** o backend não emite token e responde com mensagem genérica, sem escolher conta

### Requirement: Vínculo Google é automático por e-mail verificado e estável pelo sub
No primeiro login Google de uma identidade, o sistema SHALL vincular automaticamente o identificador Google (`sub`) a essa identidade quando o e-mail verificado normalizado corresponder a exatamente uma identidade e reserva coerentes, sem exigir senha. Um `sub` SHALL estar vinculado a no máximo uma identidade, e uma identidade a no máximo um `sub`. Acessos seguintes SHALL ser resolvidos pelo `sub` vinculado, e a mudança do e-mail na conta Google SHALL NOT transferir o acesso para outra identidade. O vínculo SHALL registrar data de criação e de último uso e SHALL NOT armazenar tokens do Google.

#### Scenario: Primeiro acesso cria vínculo
- **GIVEN** um tutor sem vínculo Google
- **WHEN** ele entra com uma conta Google de mesmo e-mail verificado
- **THEN** o backend grava o vínculo entre o `sub` e o tutor e emite a sessão, sem pedir senha

#### Scenario: Acesso seguinte usa o sub
- **GIVEN** um `sub` vinculado a um veterinário
- **WHEN** a conta Google passa a informar outro e-mail e entra novamente
- **THEN** o backend autentica o mesmo veterinário pelo `sub`, sem buscar identidade pelo novo e-mail

#### Scenario: Identidade já vinculada a outra conta Google
- **GIVEN** uma identidade vinculada a um `sub`
- **WHEN** outra conta Google com o mesmo e-mail verificado tenta entrar
- **THEN** o backend nega o acesso com mensagem genérica e mantém o vínculo original

#### Scenario: Vínculo para identidade inexistente
- **GIVEN** um `sub` vinculado a uma identidade que não existe mais ou cuja reserva diverge
- **WHEN** a conta Google tenta entrar
- **THEN** o backend não emite token

### Requirement: Estado OAuth é de uso único e amarrado à sessão do navegador
O sistema SHALL iniciar cada login Google com `state` aleatório e PKCE gerados no backend, armazenados somente como hash e verificador internos, com expiração de 10 minutos e `redirect_uri` lida da configuração do ambiente. O backend SHALL consumir o `state` antes de trocar o código, de modo que cada tentativa seja aceita no máximo uma vez. O frontend SHALL comparar o `state` retornado com o guardado na sessão da própria aba antes de chamar o backend. Segredos do cliente OAuth SHALL permanecer exclusivamente no backend.

#### Scenario: State repetido
- **GIVEN** um retorno Google já processado
- **WHEN** o mesmo `state` e código são enviados novamente
- **THEN** o backend nega sem emitir token

#### Scenario: State expirado ou desconhecido
- **WHEN** o retorno chega após a expiração ou com `state` que o backend não gerou
- **THEN** o acesso é negado com mensagem genérica

#### Scenario: Retorno iniciado em outro navegador
- **GIVEN** uma pessoa que não iniciou login Google na aba atual
- **WHEN** a rota de retorno é aberta com `code` e `state` de outra sessão
- **THEN** o frontend descarta o retorno sem chamar o backend e não cria sessão

### Requirement: Sessão Google segue o mesmo isolamento e limpeza
O sistema SHALL confirmar a identidade emitida pelo Google no endpoint protegido do perfil (`tutor/me` ou `veterinario/me`) antes de publicar a sessão e SHALL aplicar a mesma limpeza por geração do login por senha. Respostas de um login Google iniciado em sessão encerrada SHALL NOT preencher a sessão atual, e falha no login Google SHALL NOT preservar identidade anterior.

#### Scenario: Token Google veterinário em operação de tutor
- **GIVEN** um token emitido pelo login Google para um veterinário
- **WHEN** ele é enviado a uma operação protegida de pets do tutor
- **THEN** o backend nega a operação

#### Scenario: Logout durante o retorno Google
- **GIVEN** um retorno Google em processamento
- **WHEN** a sessão é encerrada antes da resposta do backend
- **THEN** a resposta é descartada e nenhuma identidade é publicada
