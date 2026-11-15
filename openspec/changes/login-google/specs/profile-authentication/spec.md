## ADDED Requirements

### Requirement: Login com Google autentica somente identidades existentes
O sistema SHALL permitir que tutor e veterinário entrem com Google, conduzindo no backend a troca do código de autorização, a validação das claims do Google (`iss`, `aud`, `exp`, `sub` e `email_verified`) e a emissão do token. O token SHALL ser gerado contra a tabela da identidade resolvida, com o mesmo perfil, claims e validade do login por senha, e a sessão SHALL ser entregue no mesmo formato (`authToken`, `perfil`, `identidade_id`). O fluxo Google SHALL NOT criar tutor, veterinário, registros em `user` ou reservas de e-mail, e SHALL NOT aceitar perfil, e-mail ou identificador enviados pelo cliente.

#### Scenario: Tutor vinculado entra com Google
- **GIVEN** um tutor cadastrado cuja conta Google já está vinculada
- **WHEN** ele conclui o login Google
- **THEN** recebe sessão de tutor sem digitar senha e é encaminhado à área do tutor

#### Scenario: Veterinário vinculado entra com Google
- **GIVEN** um veterinário cadastrado cuja conta Google já está vinculada
- **WHEN** ele conclui o login Google
- **THEN** recebe sessão de veterinário sem digitar senha e é encaminhado à área veterinária

#### Scenario: Conta Google sem cadastro
- **WHEN** o e-mail Google não corresponde a nenhuma identidade
- **THEN** o backend não emite token, não pede senha nem cria conta
- **AND** a pessoa é orientada a usar o cadastro ou o login por e-mail e senha

#### Scenario: E-mail Google não verificado
- **WHEN** o Google informa `email_verified` falso ou ausente para um `sub` ainda não vinculado
- **THEN** o backend nega o acesso com mensagem genérica, sem pedir senha e sem criar vínculo

#### Scenario: E-mail em dois perfis
- **WHEN** o e-mail Google corresponde a tutor e veterinário ao mesmo tempo ou a reserva de e-mail diverge da identidade
- **THEN** o backend não emite token e responde com mensagem genérica, sem escolher conta

### Requirement: Primeiro vínculo Google exige a senha da conta uma única vez
No primeiro login Google de uma identidade, o sistema SHALL NOT vincular nem emitir sessão apenas pelo e-mail verificado. Quando o `sub` não tiver vínculo e o e-mail verificado normalizado corresponder a exatamente uma identidade e reserva coerentes, o backend SHALL criar uma confirmação pendente de uso único, válida por 10 minutos e limitada a 5 tentativas de senha, e SHALL exigir a senha do Vet Tech dessa identidade. A senha SHALL ser conferida no backend contra a identidade guardada na confirmação, sem aceitar e-mail ou perfil enviados pelo cliente. Somente com a senha correta o backend SHALL gravar o vínculo do `sub` com a identidade e emitir a sessão. Senhas digitadas SHALL NOT ser persistidas nem registradas em log.

#### Scenario: Primeiro acesso pede a senha
- **GIVEN** um tutor sem vínculo Google
- **WHEN** ele conclui o login Google com uma conta de mesmo e-mail verificado
- **THEN** o backend não emite token nem cria vínculo
- **AND** solicita a confirmação da senha do Vet Tech

#### Scenario: Senha correta conclui o vínculo
- **GIVEN** uma confirmação pendente para um veterinário
- **WHEN** ele informa a senha correta do Vet Tech
- **THEN** o backend grava o vínculo entre o `sub` e o veterinário, consome a confirmação e emite a sessão

#### Scenario: Senha incorreta
- **GIVEN** uma confirmação pendente
- **WHEN** a pessoa informa uma senha incorreta
- **THEN** o backend não emite token nem cria vínculo, responde com a mesma mensagem do login por senha e conta a tentativa

#### Scenario: Tentativas esgotadas ou confirmação expirada
- **WHEN** a confirmação passa de 10 minutos, já foi usada ou acumulou 5 senhas incorretas
- **THEN** o backend nega qualquer nova tentativa com ela e a pessoa precisa reiniciar o login pelo Google

#### Scenario: Identidade alterada antes da confirmação
- **GIVEN** uma confirmação pendente
- **WHEN** a identidade deixa de existir, muda de e-mail ou a reserva passa a divergir antes do envio da senha
- **THEN** o backend invalida a confirmação e não emite token

### Requirement: Vínculo Google é estável pelo sub
Um `sub` SHALL estar vinculado a no máximo uma identidade, e uma identidade a no máximo um `sub`. Acessos seguintes SHALL ser resolvidos pelo `sub` vinculado, sem pedir senha, e a mudança do e-mail na conta Google SHALL NOT transferir o acesso para outra identidade. O vínculo SHALL registrar a data de criação e a de último uso e SHALL NOT armazenar tokens do Google.

#### Scenario: Acesso seguinte usa o sub
- **GIVEN** um `sub` vinculado a um veterinário
- **WHEN** a conta Google passa a informar outro e-mail e entra novamente
- **THEN** o backend autentica o mesmo veterinário pelo `sub`, sem pedir senha e sem buscar identidade pelo novo e-mail

#### Scenario: Identidade já vinculada a outra conta Google
- **GIVEN** uma identidade vinculada a um `sub`
- **WHEN** outra conta Google com o mesmo e-mail verificado tenta entrar
- **THEN** o backend nega o acesso com mensagem genérica, sem pedir senha, e mantém o vínculo original

#### Scenario: Vínculo para identidade inexistente
- **GIVEN** um `sub` vinculado a uma identidade que não existe mais ou cuja reserva diverge
- **WHEN** a conta Google tenta entrar
- **THEN** o backend não emite token

### Requirement: Estado OAuth e confirmação são de uso único e amarrados à sessão do navegador
O sistema SHALL iniciar cada login Google com `state` aleatório e PKCE gerados no backend, armazenados somente como hash e verificador internos, com expiração de 10 minutos e `redirect_uri` lida da configuração do ambiente. O backend SHALL consumir o `state` antes de trocar o código, de modo que cada tentativa seja aceita no máximo uma vez, e SHALL guardar a confirmação de vínculo somente como hash. O frontend SHALL comparar o `state` retornado com o guardado na sessão da própria aba antes de chamar o backend e SHALL manter a confirmação apenas no estado do servidor dessa aba. Segredos do cliente OAuth SHALL permanecer exclusivamente no backend.

#### Scenario: State repetido
- **GIVEN** um retorno Google já processado
- **WHEN** o mesmo `state` e código são enviados novamente
- **THEN** o backend nega sem chamar o Google e sem emitir token

#### Scenario: State expirado ou desconhecido
- **WHEN** o retorno chega após a expiração ou com `state` que o backend não gerou
- **THEN** o acesso é negado com mensagem genérica

#### Scenario: Retorno iniciado em outro navegador
- **GIVEN** uma pessoa que não iniciou login Google na aba atual
- **WHEN** a rota de retorno é aberta com `code` e `state` de outra sessão
- **THEN** o frontend descarta o retorno sem chamar o backend e não cria sessão

#### Scenario: Confirmação reutilizada
- **GIVEN** uma confirmação de vínculo já usada com sucesso
- **WHEN** ela é enviada novamente com qualquer senha
- **THEN** o backend nega sem emitir token

### Requirement: Sessão Google segue o mesmo isolamento e limpeza
O sistema SHALL confirmar a identidade emitida pelo Google no endpoint protegido do perfil (`tutor/me` ou `veterinario/me`) antes de publicar a sessão e SHALL aplicar a mesma limpeza por geração do login por senha. Respostas de um login Google ou de uma confirmação de senha iniciados em sessão encerrada SHALL NOT preencher a sessão atual, e falha no login Google SHALL NOT preservar identidade anterior.

#### Scenario: Token Google veterinário em operação de tutor
- **GIVEN** um token emitido pelo login Google para um veterinário
- **WHEN** ele é enviado a uma operação protegida de pets do tutor
- **THEN** o backend nega a operação

#### Scenario: Logout durante o retorno ou a confirmação
- **GIVEN** um retorno Google ou uma confirmação de senha em processamento
- **WHEN** a sessão é encerrada antes da resposta do backend
- **THEN** a resposta é descartada, a confirmação pendente é apagada da aba e nenhuma identidade é publicada
