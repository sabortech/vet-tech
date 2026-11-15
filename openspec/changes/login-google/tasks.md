# Tarefas

## 1. Configuração externa

- [ ] 1.1 Criar cliente OAuth "Aplicativo da Web" de teste no Google Cloud Console, com tela de consentimento em modo de teste, escopos `openid email profile` e URI de redirecionamento da rota `/login/google` do ambiente local/teste; registrar o procedimento (sem valores) em `docs/`.
- [ ] 1.2 Cadastrar `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` e `GOOGLE_OAUTH_REDIRECT_URI` nas variáveis do workspace Xano de teste; adicionar `GOOGLE_LOGIN_ENABLED=false` ao `.env.example`, junto das variáveis existentes; conferir que nenhum valor aparece no repositório.

## 2. Backend Xano

- [ ] 2.1 Criar em `xano/table/` as tabelas `tentativa_oauth_google` (hash do state, code_verifier interno, expiração, uso), `confirmacao_vinculo_google` (hash da confirmação único, sub, e-mail, perfil, identidade_id, expiração, tentativas, uso) e `vinculo_google` (sub único, perfil + identidade_id com par único, e-mail no vínculo, datas), todas não autenticáveis e com campos internos; verificar os índices únicos no ambiente de teste.
- [ ] 2.2 Implementar `GET acesso/google/inicio` no grupo Authentication, com state aleatório, PKCE S256, expiração de 10 min e `redirect_uri` lido do ambiente; testar que a resposta contém somente a URL e que o state persiste apenas como hash.
- [ ] 2.3 Implementar `POST acesso/google/retorno`: consumo único do state antes da troca do código, troca com segredo e verificador, validação de `iss`, `aud`, `exp`, `sub` e `email_verified`; `sub` vinculado → token igual ao de `acesso/login` (`resultado: "sessao"`); `sub` sem vínculo com identidade única e coerente → cria confirmação pendente e responde `resultado: "confirmar_senha"` sem token nem vínculo. Conferir na documentação XanoScript atual a função de decodificação do `id_token` antes de escrever.
- [ ] 2.4 Implementar `POST acesso/google/confirmar {confirmacao, password}`: confirmação válida, não usada, não expirada e com menos de 5 tentativas; releitura da identidade e da reserva; `security.check_password` contra a senha da identidade da confirmação; incremento de tentativas em erro; em sucesso, consumo da confirmação, criação do vínculo e emissão do token na mesma transação.
- [ ] 2.5 Testar no ambiente de teste os casos negativos: state ausente, repetido, expirado ou de outra tentativa; `error` do Google; e-mail não verificado; e-mail sem conta; e-mail nos dois perfis; reserva divergente; identidade já vinculada a outro `sub`; `sub` vinculado a identidade removida; confirmação repetida, expirada, de outro fluxo ou após 5 senhas erradas; senha correta de outra conta; identidade alterada entre retorno e confirmação. Todos sem token, sem vínculo e com mensagem genérica, sem tokens Google, senhas ou e-mails em log.
- [ ] 2.6 Provar o isolamento: token emitido via Google (primeiro acesso e acesso seguinte) para veterinário é negado em endpoints de tutor (e o inverso), e `tutor/me`/`veterinario/me` aceitam o token do perfil correto.

## 3. Frontend Reflex

- [ ] 3.1 Adicionar a leitura de `GOOGLE_LOGIN_ENABLED` em `shared/config.py` (padrão desligado) e incluir as novas mensagens genéricas na lista segura de `shared/xano_client.py` com `_CLINICAL_MESSAGES.append(...)`.
- [ ] 3.2 Extrair de `State.login` a rotina de publicação de sessão (confirmação em `{perfil}/me`, geração, carga de espécies e pets) para reutilizá-la nos caminhos Google sem duplicação; executar os testes unitários existentes de login.
- [ ] 3.3 Implementar `start_google_login` (chama `inicio`, guarda o state na sessão da aba, redireciona), `finish_google_login` (compara o state, limpa-o, chama `retorno`, publica a sessão ou entra na etapa de senha guardando `confirmacao`) e `confirm_google_link` (envia `confirmacao` + senha, publica a sessão, mantém a etapa em senha incorreta, volta a `/login` em confirmação expirada) e `cancel_google_link`; cobrir com testes unitários: state divergente/ausente, `error` na query, resposta atrasada após logout, falha do Xano, primeiro acesso com senha correta e incorreta, confirmação expirada, acesso seguinte sem senha, para tutor e veterinário.
- [ ] 3.4 Tornar o botão de `components/auth.py` acionável e acessível quando a flag estiver ligada (desabilitado durante envio) e inerte quando desligada; criar a página `/login/google` em `pages/`, com estados de carregamento, confirmação de senha e redirecionamento, usando o mesmo cartão com LED e as imagens otimizadas do login, registrada em `vet_tech.py`; compilar conforme a skill de processos Reflex.

## 4. Verificação conjunta e implantação

- [ ] 4.1 Percorrer no navegador, em ambiente de teste com usuários de teste Google: tutor e veterinário existentes (primeiro acesso pede a senha uma vez e cria o vínculo; segundo acesso entra sem senha pelo `sub`), senha errada no primeiro acesso, cancelamento na etapa de senha, e-mail sem conta (orientação de cadastro), cancelamento no Google, flag desligada; desktop e celular sem overflow. Registrar em `verification.md` sem dados pessoais.
- [ ] 4.2 Confirmar a regressão do login por e-mail e senha, do cadastro e do logout; verificar que nenhum registro foi criado em `user`, `tutor` ou `veterinario` pelo fluxo Google.
- [ ] 4.3 Atualizar `docs/architecture.md` (fluxo OAuth no Xano, confirmação de senha no primeiro acesso e rota de retorno) e documentar as variáveis; publicar em produção somente depois de configurar o cliente OAuth de produção e habilitar a flag por último, registrando o procedimento de rollback (desligar a flag).
