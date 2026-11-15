# Verificação — login-google

Sem dados pessoais: identidades citadas apenas por perfil e id interno de teste.

## Ambiente

- Xano: workspace 167758, branch live `v1` (sem branch de teste; publicação autorizada pelo usuário em 2026-11-15).
- Reflex local em `http://localhost:3000`, `GOOGLE_LOGIN_ENABLED=true` no `.env` local.
- Cliente OAuth de teste no Google Cloud (tela de consentimento em modo de teste), URI `http://localhost:3000/login/google`.

## Backend (chamadas diretas, 2026-11-15)

| Caso | Resultado |
|---|---|
| `GET acesso/google/inicio` | 200, resposta só com `url`; `client_id`, `redirect_uri`, escopos, `prompt=select_account`, `code_challenge_method=S256`; `state` e `code_challenge` com 43 caracteres base64url |
| `retorno` com `state` inventado | 403, mensagem genérica |
| `retorno` com `state` real e `code` falso, duas vezes | 403 genérico nas duas (troca recusada pelo Google; `state` consumido) |
| Campos vazios | 400 do Xano (`Missing param`); o Reflex nunca envia vazio |

Bugs encontrados e corrigidos antes do teste real: padding `.` do `base64_encode_urlsafe` do Xano no PKCE; campos `internal` não retornados por `db.get` sem `output`.

## Navegador com conta Google de teste (tutor, identidade 54)

| Caso | Resultado |
|---|---|
| Flag desligada | Elemento Google inerte (não é botão) |
| Botão com flag ligada | Leva à tela do Google "Prosseguir para Vet Tech", sem erro de URI |
| Primeiro acesso (sem vínculo) | Entrou direto na área do tutor, sem pedir senha; `vinculo_google` criado às 18:59:30 com perfil `tutor` e `sub` preenchido; nenhum marcador de confirmação novo |
| Acesso seguinte (vínculo existente) | Entrou pelo `sub` sem senha; `ultimo_uso_em` atualizado (18:54:35, antes de o vínculo de teste ser apagado e recriado) |
| Veterinário, primeiro acesso (identidade 18) | Entrou direto na área veterinária, sem senha; `vinculo_google` criado às 19:05:56 com perfil `veterinario`; nenhum registro novo em `tutor`, `veterinario` ou `reserva_email` |
| Conta Google sem cadastro (19:03) | Volta a `/login` com "Não encontramos uma conta Vet Tech para esta conta Google. Faça seu cadastro ou entre com e-mail e senha.", sem sessão; nenhum registro novo em `tutor`, `veterinario`, `user`, `reserva_email` ou `vinculo_google` (o mais recente de cada é anterior ao teste); só o marcador `state` da tentativa |
| Cancelamento no Google (19:11) | Fluxo iniciado no navegador do app; retorno reproduzido exatamente como o Google o envia ao cancelar (`/login/google?error=access_denied&state=<state da aba>`), já que as contas de teste não mostram mais consentimento. Volta a `/login` com "Não foi possível entrar com o Google. Tente novamente.", sem sessão, formulário e botão Google utilizáveis; `retorno` não foi chamado (nenhum marcador `state` novo no Xano) |
| `/login/google` com `code`/`state` forjados | Volta a `/login` com "Não foi possível entrar com o Google. Tente novamente.", sem sessão; sem overflow em 375 px |

## Isolamento dos tokens (tarefa 2.6, 19:15)

Tokens gerados com `xano function run "Identity/issue_session"`, a mesma função que o `retorno` do Google usa, para as identidades de teste veterinário 18 e tutor 54 (tokens não impressos nem gravados). O frontend já barra perfis trocados antes de chamar o Xano, por isso o teste foi feito direto na API.

| Token | Endpoint | HTTP |
|---|---|---|
| veterinário | `veterinario/me` | 200 |
| veterinário | `veterinario/agenda` | 200 |
| veterinário | `tutor/me` | 401 |
| veterinário | `pets` (tutor) | 401 |
| tutor | `tutor/me` | 200 |
| tutor | `pets` (tutor) | 200 |
| tutor | `veterinario/me` | 401 |
| tutor | `veterinario/agenda` | 401 |

## Regressão (tarefa 4.2)

- Login por e-mail e senha seguido de logout, feito pelo usuário com conta de teste: entrou na área do perfil e o logout voltou a `/login` sem sessão.
- `/cadastro` abre com os campos, o seletor de perfil e "Cadastrar", sem erros no console.
- Testes de login, logout, cadastro e Google: 22 passam; os testes antigos do login por senha passam sem alteração após a extração de `_open_session`.
- Nenhum registro criado pelo fluxo Google em `user`, `tutor`, `veterinario` ou `reserva_email` (registros mais recentes anteriores aos testes com Google).

## Casos negativos (tarefa 2.5)

Testes unitários do Xano, escritos dentro de `retorno_POST.xs` e das funções `Identity/*` com `mock` para o Google e para toda gravação (ids simulados `-1`; o `db.del` da tentativa, que não aceita `mock`, ficou em `try_catch`, pois o uso único já é garantido pelo marcador). Rodados com `xano unit_test run_all`: **18 passam, 0 falham**. As tabelas do Google, `tutor` e `veterinario` ficaram idênticas antes e depois da execução.

| Construção | Teste | Resultado esperado |
|---|---|---|
| `retorno` | nega state desconhecido ou expirado | erro genérico |
| `retorno` | nega email google nao verificado | erro genérico, sem vínculo |
| `retorno` | orienta cadastro quando nao ha conta | mensagem de cadastro |
| `retorno` | nega email em dois perfis ou reserva divergente | erro genérico |
| `retorno` | nega identidade ja vinculada a outro sub | erro genérico |
| `retorno` | nega vinculo de identidade removida | erro genérico |
| `retorno` | nega claims invalidas do google | erro genérico |
| `retorno` | cria vinculo no primeiro acesso sem senha | `resultado: "sessao"` |
| `retorno` | entra pelo sub ja vinculado | `resultado: "sessao"` |
| `resolve_login_email` | tutor / veterinário único com reserva coerente | `ok` com o perfil certo |
| `resolve_login_email` | sem conta em nenhum perfil | `sem_conta` |
| `resolve_login_email` | email nos dois perfis; reserva divergente; reserva ausente | `conflito` |
| `linked_identity_valid` | identidade removida; reserva divergente | `false` |
| `linked_identity_valid` | identidade coerente | `true` |

Cada teste negativo do `retorno` difere do teste de sucesso em um único ponto simulado, então falha exatamente na verificação que pretende cobrir. Depois da publicação, o fluxo real com `state` válido e `code` falso continua respondendo 403 genérico nas duas tentativas.

## Testes automatizados

- `tests/unit/test_google_login.py`: 10 testes (com subtestes) do fluxo Google no estado Reflex.
- Suíte unitária: 383 passam; 3 falhas preexistentes e sem relação (2 por falta de `pypdf` no `.venv`, 1 de tempo em `test_interface_performance`, que falha igual com o código da `main`).
