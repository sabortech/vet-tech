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
- 2026-11-12: Google disponível para **tutor e veterinário**; **somente contas existentes**; vínculo automático por e-mail verificado.
- 2026-11-15: por um período, o primeiro vínculo exigiu a senha do Vet Tech; no mesmo dia o usuário revogou essa decisão. **O login Google não pede a senha do Vet Tech em nenhum momento**, e o primeiro vínculo volta a ser automático por e-mail verificado.

## Goals / Non-Goals

**Goals:**
- Entrar pelo Google em contas existentes dos dois perfis, chegando à mesma sessão produzida pelo login por senha, sem digitar a senha do Vet Tech.
- Manter no Xano toda decisão de identidade: validação do Google, resolução do perfil, vínculo e emissão do token.
- Proteger o fluxo contra CSRF de login, reutilização de código/estado e confusão de contas.

**Non-Goals:**
- Criar contas pelo Google ou pré-preencher cadastro.
- Desvincular, trocar conta Google ou listar vínculos na interface.
- Remover a senha das contas ou permitir contas sem senha.
- Mudanças no fluxo de recuperação de senha.
- Outros provedores, Google One Tap, refresh tokens ou acesso a APIs Google além da identidade.

## Decisions

### 1. OAuth no Xano, Reflex apenas como navegador

Fluxo de código de autorização (OpenID Connect) com PKCE, conduzido pelo Xano:

1. O Reflex chama `GET acesso/google/inicio`. O Xano gera `state` e `code_verifier` aleatórios, grava `tentativa_oauth_google` (hash do `state`, `code_verifier`, `expira_em` = agora + 10 min) e devolve somente `{url}` (o Reflex extrai o `state` dessa URL), montada com `client_id`, `redirect_uri` do ambiente, `response_type=code`, `scope=openid email profile`, `state`, `code_challenge` (S256) e `prompt=select_account`.
2. O Reflex guarda o `state` recebido no estado do servidor da aba e redireciona o navegador para `url`.
3. O Google redireciona para a rota Reflex `/login/google` com `code` e `state` (ou `error`).
4. O Reflex confere se o `state` da query é igual ao guardado na sessão da aba (amarração ao navegador contra CSRF de login), descarta-o e chama `POST acesso/google/retorno {code, state}`.
5. O Xano localiza a tentativa pelo hash do `state`, exige que não esteja expirada e a consome **antes** de chamar o Google (marcador de uso único, ver seção 3; a linha da tentativa é apagada), de modo que o uso é único mesmo em falha. Troca o código em `https://oauth2.googleapis.com/token` com `client_secret` e `code_verifier`, valida o `id_token`, resolve a identidade, cria o vínculo se for o primeiro acesso (seção 3) e responde `{resultado: "sessao", authToken, perfil, identidade_id}`, com o mesmo conteúdo de `acesso/login`.
6. O Reflex executa a rotina pós-login (confirmação em `{perfil}/me`, limpeza por geração, carga de espécies e pets do tutor), extraída do evento `login` existente para não duplicar a publicação de sessão.

Alternativas rejeitadas:
- *OAuth no servidor Reflex* (ex.: biblioteca Authlib): exigiria o segredo do cliente no Reflex e levaria a decisão de identidade para fora do Xano, contrariando "autorização no backend"; também introduziria dependência nova.
- *Google Identity Services no navegador enviando o `id_token` ao Xano*: dispensa o segredo, mas exige validar assinatura JWT com JWKS no Xano e expõe o fluxo a scripts de terceiros na página; o fluxo de código mantém o navegador fora da obtenção do token.
- *Extensão/snippet de Google OAuth do marketplace Xano*: pode servir de referência, mas os endpoints devem seguir os contratos desta change (PKCE, `state` persistido de uso único, resolução por `reserva_email`) e não podem criar registros em `user`.
- *Confirmar a senha do Vet Tech no primeiro vínculo*: implementada e depois descartada por decisão de produto (2026-11-15); ver riscos.

### 2. Validação do `id_token`

O `id_token` é obtido diretamente do endpoint de token do Google por TLS, autenticado com o segredo do cliente; pelo OpenID Connect Core (3.1.3.7), a validação TLS dispensa a verificação de assinatura nesse caso. Mesmo assim, o Xano SHALL validar as claims: `iss` ∈ {`https://accounts.google.com`, `accounts.google.com`}, `aud` = `GOOGLE_OAUTH_CLIENT_ID`, `exp` no futuro, `sub` não vazio, `email` presente e `email_verified = true`. O payload é lido com `split` + `base64_decode_urlsafe` + `json_decode`.

Tokens do Google (`access_token`, `id_token`) não são persistidos nem registrados em log.

### 3. Resolução da identidade e vínculo automático

Tabelas técnicas novas (não autenticáveis, campos internos lidos sempre com `output` explícito):

- `vinculo_google`: `google_sub` (único), `perfil`, `identidade_id`, `email_no_vinculo`, `created_at`, `ultimo_uso_em`; índice único também em `(perfil, identidade_id)`, para impedir duas contas Google na mesma identidade.
- `tentativa_oauth_google`: `state_hash` (único), `code_verifier`, `expira_em`, `created_at`. A linha é apagada ao ser consumida.
- `uso_oauth_google`: `chave` (única), `created_at`. Marcador de uso único no mesmo padrão de `support_lock`/`clinical_lock`: inserir uma chave já existente falha no índice único, então só uma requisição concorrente passa. Chave usada: `state:<id da tentativa>`.

Funções compartilhadas em `function/identity/`: `resolve_login_email` (regras de identidade de `acesso/login` sem a senha, com situação `ok`/`sem_conta`/`conflito`), `linked_identity_valid` (vínculo ainda aponta para identidade coerente) e `issue_session` (mesmo token de `acesso/login`). O endpoint `acesso/login` não foi alterado.

Ordem de resolução em `acesso/google/retorno`:

1. **`sub` já vinculado**: usa `perfil` + `identidade_id` do vínculo, confirma que a identidade ainda existe e que `reserva_email` continua apontando para ela, atualiza `ultimo_uso_em` e emite o token. O e-mail atual do Google não é usado para trocar de conta.
2. **`sub` sem vínculo**: normaliza o e-mail (trim + minúsculas), exige `email_verified = true` e aplica as mesmas regras de `acesso/login`: exatamente uma identidade entre `tutor` e `veterinario`, com reserva existente e coerente. Cria `vinculo_google` (os índices únicos em `google_sub` e em `(perfil, identidade_id)` rejeitam identidade já vinculada a outro `sub` ou vínculo concorrente, e a falha vira mensagem genérica) e emite o token. Não pede senha.
3. Qualquer falha (e-mail desconhecido, duplicidade entre perfis, reserva divergente, e-mail não verificado, vínculo conflitante, estado inválido, erro do Google) responde com mensagem genérica, sem revelar se a conta existe. Somente o caso "nenhuma conta com este e-mail Google" recebe a orientação de cadastro, também genérica: "Não encontramos uma conta Vet Tech para esta conta Google. Faça seu cadastro ou entre com e-mail e senha."

   Observação: essa orientação diferencia "sem conta" de outras falhas para um e-mail Google **que a própria pessoa controla**. É o mesmo nível de informação que o cadastro já revela ao rejeitar e-mail repetido e não permite consultar e-mails de terceiros.

O token é gerado com `security.create_auth_token` contra `tutor` ou `veterinario`, com os mesmos `extras = {perfil}` e a mesma expiração de 86400 s do login por senha. Nenhum endpoint passa a aceitar outro formato de token.

Particularidades do Xano observadas na implementação: `base64_encode_urlsafe` usa `.` como padding (removido junto com `=` para o PKCE); `db.get` só devolve campos `visibility = "internal"` listados em `output`; o push normaliza o arquivo e descarta valores padrão como `?=0`, por isso os inserts gravam todos os campos explicitamente.

### 4. Reflex

- `GOOGLE_LOGIN_ENABLED` (padrão desligado) controla se o botão é acionável, e o evento confere a flag de novo no servidor. Desligado, o botão mantém a aparência atual, sem ação e sem afirmar disponibilidade.
- O botão vira `rx.button` acessível ("Entrar com Google"), desabilitado durante `is_busy`, que dispara `start_google_login`.
- A nova rota `/login/google` (página em `pages/`) tem `on_load` que executa `finish_google_login`, lendo `code`, `state` e `error` da query. Ela reutiliza o cartão da autenticação (`auth_shell`: LED de perímetro, `auth-led-card`, fundo `/optimized/fundo02.webp`) e mostra apenas o indicador de carregamento (`role="status"`). Ao publicar a sessão, redireciona para `/`, que renderiza a área do perfil como no login por senha; em erro, redireciona para `/login` com a mensagem em `login_message`.
- O `state` pendente vive no estado do servidor (nunca em query nem em localStorage) e é limpo em logout, troca de sessão, erro e conclusão. `code` nunca é registrado nem guardado além da requisição. Uma abertura de `/login/google` sem `state` pendente na aba é tratada como retorno inválido; se já houver sessão ativa, apenas volta para `/` sem deslogar.
- Novas mensagens do Xano entram na lista segura de `xano_client.py` pelo mesmo padrão `_CLINICAL_MESSAGES`.

### 5. Variáveis de ambiente

| Onde | Variável | Uso |
|---|---|---|
| Xano | `GOOGLE_OAUTH_CLIENT_ID` | `client_id` na URL de autorização e verificação de `aud` |
| Xano | `GOOGLE_OAUTH_CLIENT_SECRET` | troca do código no endpoint de token (segredo) |
| Xano | `GOOGLE_OAUTH_REDIRECT_URI` | URI exata da rota Reflex `/login/google` do ambiente; nunca recebida do cliente |
| Reflex `.env` | `GOOGLE_LOGIN_ENABLED` | `true`/`false`; habilita o botão |

O `.env.example` documenta somente a flag do Reflex, ao lado das variáveis já existentes. Os valores do Xano ficam nas variáveis de ambiente do workspace (`$env.*`), com um cliente OAuth por ambiente e sua URI registrada no Google Cloud Console.

## Risks / Trade-offs

- [Vínculo automático confia só no e-mail verificado pelo Google] → Quem controla uma conta Google com o mesmo e-mail de uma conta Vet Tech entra nela sem saber a senha (ex.: administrador de um domínio Google Workspace que recria um endereço, ou e-mail reciclado). Mitigação: exigir `email_verified`, vincular ao `sub` no primeiro uso para que trocas posteriores de e-mail no Google não migrem a sessão, e registrar `created_at`/`ultimo_uso_em`. Risco aceito pela decisão de produto de 2026-11-15; aviso por e-mail a cada novo vínculo fica como melhoria futura.
- [Primeiro acesso diferencia "sem conta" de outras falhas] → Só para o e-mail Google que a pessoa controla e já verificou; equivalente ao que o cadastro revela.
- [Contas com e-mail duplicado entre perfis] → Seguem bloqueadas como no login por senha; nenhuma escolha automática.
- [Redefinir a senha não remove o vínculo] → O vínculo depende do `sub`, não da senha; desvincular fica fora do escopo.
- [`state` perdido ao trocar de aba ou reiniciar o servidor Reflex] → O retorno falha com mensagem genérica e a pessoa reinicia o fluxo; tentativas expiram em 10 min.
- [Variáveis ausentes ou erradas no Xano] → `inicio` falha de forma genérica; a flag no Reflex permite manter o botão desligado até a configuração do ambiente ser verificada.
- [Dependência de rede com o Google] → Timeout e erro são tratados como falha genérica; o login por senha continua disponível.

## Migration Plan

1. Tabelas e endpoints publicados na branch live (`v1`) do Xano em 2026-11-15, por decisão do usuário (não há branch de teste). São aditivos e ficam sem uso enquanto a flag do Reflex estiver desligada.
2. Remover do workspace o que sobrou da etapa de senha descartada: endpoint `acesso/google/confirmar` e tabela `confirmacao_vinculo_google` (vazia, sem uso).
3. Implementar o Reflex com `GOOGLE_LOGIN_ENABLED=false`; publicar o frontend sem efeito visível.
4. Verificar o fluxo e os casos negativos com usuários de teste Google (ver tarefas) e registrar em `verification.md`.
5. Configurar cliente OAuth de produção e só então habilitar a flag.
6. Rollback: desligar `GOOGLE_LOGIN_ENABLED`; os endpoints podem permanecer sem uso. Tabelas e vínculos são mantidos (não afetam o login por senha) e não são truncados.

## Open Questions

- Validar com o usuário, antes de publicar em produção, se deseja aviso por e-mail a cada novo vínculo Google (exigiria change própria de notificações).
- Limpeza periódica de `tentativa_oauth_google` expiradas: tarefa agendada no Xano agora ou em change futura.
