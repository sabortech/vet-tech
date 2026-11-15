# Design

## Context

Ver `proposal.md`. O login atual é `POST acesso/login` no grupo Authentication: o Xano normaliza o e-mail, exige exatamente uma identidade entre `tutor` e `veterinario`, confere a `reserva_email` correspondente (perfil + `identidade_id`), valida a senha (`tutor.password` ou `veterinario.senha`) e emite `security.create_auth_token` contra a própria tabela, com `extras = {perfil}` e validade de 86400 s. O Reflex (`features/auth/state.py::login`) limpa a sessão, valida a resposta `{authToken, perfil, identidade_id}`, confirma a identidade em `{perfil}/me`, publica a sessão e, para tutor, carrega espécies e pets, descartando respostas de gerações antigas.

`components/auth.py` renderiza "Entrar com Google" como elemento decorativo (`cursor="default"`), e a spec `login-screen-presentation` proíbe afirmar que o fluxo existe. Não há código OAuth no projeto. O cliente HTTP (`shared/xano_client.py`) só repassa mensagens de erro de uma lista segura (`_CLINICAL_MESSAGES`, ampliada com `append`).

Mudanças recebidas na `main` até `f32239c` que afetam esta change:
- O cartão de login ganhou LED de perímetro e sombra verde (`perimeter_led(...)`, classe `auth-led-card`), exigidos pela spec `auth-decoration` para login e cadastro.
- As imagens da autenticação passaram a ser servidas de `/optimized/*.webp` (spec `interface-performance`).
- `xano_client.py` ganhou `xano_request_batch()` para reutilizar conexão dentro de uma operação.
- O tutor autenticado é levado à escolha de pet por `/?selecionar=pet` e ao Dashboard por `/dashboard`. O evento `login` em si não mudou e não redireciona: `/` e `/login` renderizam a área do perfil quando `is_authenticated`.

Decisões de produto:
- 2026-11-12: Google disponível para **tutor e veterinário**; **somente contas existentes**.
- 2026-11-15 (substitui o vínculo automático de 2026-11-12): **no primeiro login Google a pessoa digita a senha do Vet Tech uma única vez** para confirmar o vínculo; depois disso, o Google entra sem senha.

## Goals / Non-Goals

**Goals:**
- Entrar pelo Google em contas existentes dos dois perfis, chegando à mesma sessão produzida pelo login por senha.
- Exigir prova de posse da conta Vet Tech (senha) antes do primeiro vínculo, sem depender só do e-mail verificado pelo Google.
- Manter no Xano toda decisão de identidade: validação do Google, resolução do perfil, conferência da senha, vínculo e emissão do token.
- Proteger o fluxo contra CSRF de login, reutilização de código/estado/confirmação, força bruta de senha na confirmação e confusão de contas.

**Non-Goals:**
- Criar contas pelo Google ou pré-preencher cadastro.
- Desvincular, trocar conta Google ou listar vínculos na interface.
- Remover a senha das contas ou permitir contas sem senha.
- Recuperação de senha dentro do fluxo Google.
- Outros provedores, Google One Tap, refresh tokens ou acesso a APIs Google além da identidade.

## Decisions

### 1. OAuth no Xano, Reflex apenas como navegador

Fluxo de código de autorização (OpenID Connect) com PKCE, conduzido pelo Xano:

1. O Reflex chama `GET acesso/google/inicio`. O Xano gera `state` e `code_verifier` aleatórios, grava `tentativa_oauth_google` (hash do `state`, `code_verifier`, `expira_em` = agora + 10 min, `usada = false`) e devolve `{url}`, montada com `client_id`, `redirect_uri` do ambiente, `response_type=code`, `scope=openid email profile`, `state`, `code_challenge` (S256) e `prompt=select_account`.
2. O Reflex guarda o `state` recebido no estado do servidor da aba e redireciona o navegador para `url`.
3. O Google redireciona para a rota Reflex `/login/google` com `code` e `state` (ou `error`).
4. O Reflex confere se o `state` da query é igual ao guardado na sessão da aba (amarração ao navegador contra CSRF de login), descarta-o e chama `POST acesso/google/retorno {code, state}`.
5. O Xano localiza a tentativa pelo hash do `state`, exige que não esteja usada nem expirada e a marca como usada **antes** de chamar o Google (uso único mesmo em falha). Troca o código em `https://oauth2.googleapis.com/token` com `client_secret` e `code_verifier`, valida o `id_token` e resolve a identidade (seção 3). Responde com um de dois formatos:
   - `{resultado: "sessao", authToken, perfil, identidade_id}`: `sub` já vinculado, mesmo conteúdo de `acesso/login`.
   - `{resultado: "confirmar_senha", confirmacao, email}`: primeiro acesso. `confirmacao` é um identificador opaco de uso único e `email` é o e-mail da própria conta Google escolhida.
6. Se for `sessao`, o Reflex executa a rotina pós-login. Se for `confirmar_senha`, guarda `confirmacao` no estado do servidor da aba, mostra a etapa de senha (seção 4) e, ao enviar, chama `POST acesso/google/confirmar {confirmacao, password}`, que responde `{authToken, perfil, identidade_id}` em caso de sucesso.
7. A rotina pós-login (confirmação em `{perfil}/me`, limpeza por geração, carga de espécies e pets do tutor) é extraída do evento `login` existente e reutilizada pelos três caminhos, sem duplicar a publicação de sessão.

Alternativas rejeitadas:
- *OAuth no servidor Reflex* (ex.: biblioteca Authlib): exigiria o segredo do cliente no Reflex e levaria a decisão de identidade para fora do Xano, contrariando "autorização no backend"; também introduziria dependência nova.
- *Google Identity Services no navegador enviando o `id_token` ao Xano*: dispensa o segredo, mas exige validar assinatura JWT com JWKS no Xano e expõe o fluxo a scripts de terceiros na página; o fluxo de código mantém o navegador fora da obtenção do token.
- *Extensão/snippet de Google OAuth do marketplace Xano*: pode servir de referência, mas os endpoints devem seguir os contratos desta change (PKCE, `state` persistido de uso único, confirmação por senha, resolução por `reserva_email`) e não podem criar registros em `user`.

### 2. Validação do `id_token`

O `id_token` é obtido diretamente do endpoint de token do Google por TLS, autenticado com o segredo do cliente; pelo OpenID Connect Core (3.1.3.7), a validação TLS dispensa a verificação de assinatura nesse caso. Mesmo assim, o Xano SHALL validar as claims: `iss` ∈ {`https://accounts.google.com`, `accounts.google.com`}, `aud` = `GOOGLE_OAUTH_CLIENT_ID`, `exp` no futuro, `sub` não vazio, `email` presente e `email_verified = true`. Antes de editar, conferir na documentação XanoScript atual a função para decodificar o payload JWT (ou usar o endpoint `tokeninfo`/`userinfo` do Google como alternativa); não escrever decodificador caseiro sem necessidade.

Tokens do Google (`access_token`, `id_token`) não são persistidos nem registrados em log.

### 3. Resolução da identidade e vínculo confirmado por senha

Tabelas técnicas novas (não autenticáveis, campos internos):

- `vinculo_google`: `google_sub` (único), `perfil`, `identidade_id`, `email_no_vinculo`, `created_at`, `ultimo_uso_em`; índice único também em `(perfil, identidade_id)`, para impedir duas contas Google na mesma identidade.
- `confirmacao_vinculo_google`: `confirmacao_hash` (único), `google_sub`, `email`, `perfil`, `identidade_id`, `expira_em` (agora + 10 min), `tentativas` (inteiro, inicia em 0), `usada`, `created_at`.

Ordem de resolução em `acesso/google/retorno`:

1. **`sub` já vinculado**: usa `perfil` + `identidade_id` do vínculo, confirma que a identidade ainda existe e que `reserva_email` continua apontando para ela, atualiza `ultimo_uso_em` e emite o token (`resultado: "sessao"`). O e-mail atual do Google não é usado para trocar de conta.
2. **`sub` sem vínculo**: normaliza o e-mail (trim + minúsculas), exige `email_verified = true` e aplica as mesmas regras de `acesso/login`: exatamente uma identidade entre `tutor` e `veterinario`, com reserva existente e coerente. Se a identidade já tiver vínculo com outro `sub`, nega. Caso contrário, **não cria vínculo nem token**: invalida confirmações pendentes anteriores do mesmo `sub`, grava `confirmacao_vinculo_google` com o hash de um identificador aleatório e responde `resultado: "confirmar_senha"`.
3. Qualquer falha (e-mail desconhecido, duplicidade entre perfis, reserva divergente, e-mail não verificado, vínculo conflitante, estado inválido, erro do Google) responde com mensagem genérica, sem revelar se a conta existe. Somente o caso "nenhuma conta com este e-mail Google" recebe a orientação de cadastro, também genérica: "Não encontramos uma conta Vet Tech para esta conta Google. Faça seu cadastro ou entre com e-mail e senha."

   Observação: essa orientação, assim como a etapa de senha, diferencia "sem conta" de "com conta" para um e-mail Google **que a própria pessoa controla**. É o mesmo nível de informação que o cadastro já revela ao rejeitar e-mail repetido e não permite consultar e-mails de terceiros.

`acesso/google/confirmar {confirmacao, password}`:

1. Localiza a confirmação pelo hash e exige que não esteja usada nem expirada e que tenha `tentativas < 5`. Falha → "Confirmação expirada. Entre com Google novamente." sem distinguir o motivo.
2. Relê a identidade (`perfil`, `identidade_id`) e confirma que ela ainda existe, que a `reserva_email` continua coerente e que o e-mail da identidade ainda é o da confirmação. Se algo mudou, marca a confirmação como usada e nega de forma genérica.
3. Confere a senha com `security.check_password` contra a senha **dessa** identidade (`tutor.password` ou `veterinario.senha`). A pessoa não informa e-mail nem perfil; os dois vêm da confirmação gravada no backend.
4. Senha incorreta: incrementa `tentativas` e responde "Credenciais inválidas." (mesma mensagem do login por senha). Ao atingir 5, a confirmação fica inutilizável e a pessoa precisa reiniciar o fluxo pelo Google.
5. Senha correta: na mesma transação, marca a confirmação como usada, verifica de novo se `sub` e identidade continuam sem vínculo, cria `vinculo_google` e emite o token. Os índices únicos de `vinculo_google` arbitram confirmações concorrentes.

O token é gerado com `security.create_auth_token` contra `tutor` ou `veterinario`, com os mesmos `extras = {perfil}` e a mesma expiração de 86400 s do login por senha. Nenhum endpoint passa a aceitar outro formato de token. A senha digitada não é persistida nem registrada em log.

### 4. Reflex

- `GOOGLE_LOGIN_ENABLED` (padrão desligado) controla se o botão é acionável. Desligado, o botão mantém a aparência atual, sem ação e sem afirmar disponibilidade, como a spec exige hoje.
- O botão vira `rx.button` acessível ("Entrar com Google"), desabilitado durante `is_busy`, que dispara `start_google_login`.
- A nova rota `/login/google` (página em `pages/`) tem `on_load` que executa `finish_google_login`, lendo `code`, `state` e `error` da query. Ela reutiliza o cartão da autenticação (LED de perímetro, `auth-led-card`, fundo `/optimized/fundo02.webp`) e tem três estados:
  - **Carregando**: indicador acessível (`role="status"`).
  - **Confirmar senha** (somente primeiro acesso): texto "Para vincular sua conta Google, confirme sua senha do Vet Tech. Isso só será pedido uma vez.", o e-mail Google em modo somente leitura, campo de senha, botão "Confirmar e entrar" (desabilitado durante envio) e link "Cancelar e voltar ao login". Senha incorreta mantém a etapa e mostra o erro; confirmação expirada ou esgotada volta a `/login` com mensagem.
  - **Concluído/erro**: ao publicar a sessão, redireciona para `/`, que renderiza a área do perfil como no login por senha. Em erro, redireciona para `/login` com a mensagem em `login_message`.
- O `state` pendente e a `confirmacao` vivem no estado do servidor (nunca em query nem em localStorage) e são limpos em logout, troca de sessão, erro, cancelamento e conclusão. `code` e senha nunca são registrados nem guardados além da requisição. Uma abertura de `/login/google` sem `state` pendente nem confirmação na aba é tratada como retorno inválido.
- Novas mensagens do Xano entram na lista segura de `xano_client.py` pelo mesmo padrão `_CLINICAL_MESSAGES.append(...)`.

### 5. Variáveis de ambiente

| Onde | Variável | Uso |
|---|---|---|
| Xano | `GOOGLE_OAUTH_CLIENT_ID` | `client_id` na URL de autorização e verificação de `aud` |
| Xano | `GOOGLE_OAUTH_CLIENT_SECRET` | troca do código no endpoint de token (segredo) |
| Xano | `GOOGLE_OAUTH_REDIRECT_URI` | URI exata da rota Reflex `/login/google` do ambiente; nunca recebida do cliente |
| Reflex `.env` | `GOOGLE_LOGIN_ENABLED` | `true`/`false`; habilita o botão |

O `.env.example` documenta somente a flag do Reflex, ao lado das variáveis já existentes (`XANO_API_BASE_URL`, `N8N_*`, `SUPPORT_CHAT_BRIDGE_SECRET`). Os valores do Xano ficam nas variáveis de ambiente do workspace (`$env.*`), com um cliente OAuth por ambiente (desenvolvimento/teste/produção) e sua URI registrada no Google Cloud Console.

## Risks / Trade-offs

- [Força bruta na confirmação de senha] → A confirmação só existe depois de um login Google válido com e-mail verificado da própria conta, expira em 10 min e aceita no máximo 5 tentativas. Novas confirmações exigem uma nova ida ao Google. A mensagem de erro é a mesma do login por senha.
- [Pessoa sem lembrar a senha não consegue o primeiro vínculo] → Aceito por decisão de produto; a recuperação de senha está fora do escopo e continua só visual. A pessoa pode cancelar e usar o login por senha, quando lembrar.
- [Primeiro acesso diferencia "com conta" de "sem conta"] → Só para o e-mail Google que a pessoa controla e já verificou; equivalente ao que o cadastro revela.
- [Contas com e-mail duplicado entre perfis] → Seguem bloqueadas como no login por senha; nenhuma escolha automática.
- [`state` ou confirmação perdidos ao trocar de aba ou reiniciar o servidor Reflex] → O retorno falha com mensagem genérica e a pessoa reinicia o fluxo; tentativas e confirmações expiram em 10 min.
- [Variáveis ausentes ou erradas no Xano] → `inicio` falha de forma genérica; a flag no Reflex permite manter o botão desligado até a configuração do ambiente ser verificada.
- [Dependência de rede com o Google] → Timeout e erro são tratados como falha genérica; o login por senha continua disponível.

## Migration Plan

1. Criar as tabelas novas (aditivas) e os endpoints em ambiente de teste; configurar cliente OAuth de teste e variáveis do workspace de teste.
2. Implementar o Reflex com `GOOGLE_LOGIN_ENABLED=false`; publicar o frontend sem efeito visível.
3. Verificar o fluxo e os casos negativos no ambiente de teste (ver tarefas) e registrar em `verification.md`.
4. Configurar cliente OAuth e variáveis de produção, publicar os endpoints e só então habilitar a flag.
5. Rollback: desligar `GOOGLE_LOGIN_ENABLED`; os endpoints podem permanecer sem uso. Tabelas e vínculos são mantidos (não afetam o login por senha) e não são truncados. Confirmações pendentes expiram sozinhas.

## Open Questions

- Validar com o usuário, antes de publicar em produção, se deseja aviso por e-mail a cada novo vínculo Google (exigiria change própria de notificações).
- Limpeza periódica de `tentativa_oauth_google` e `confirmacao_vinculo_google` expiradas: tarefa agendada no Xano agora ou em change futura.
