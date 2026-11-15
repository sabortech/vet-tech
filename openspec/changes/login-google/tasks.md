# Tarefas

## 1. Configuração externa

- [x] 1.1 Criar cliente OAuth "Aplicativo da Web" de teste no Google Cloud Console, com tela de consentimento em modo de teste, escopos `openid email profile` e URI de redirecionamento da rota `/login/google` do ambiente local/teste. Procedimento não registrado em `docs/`, por decisão do usuário.
- [x] 1.2 Cadastrar `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` e `GOOGLE_OAUTH_REDIRECT_URI` nas variáveis do workspace Xano; adicionar `GOOGLE_LOGIN_ENABLED=false` ao `.env.example`, junto das variáveis existentes; conferir que nenhum valor aparece no repositório.
- [x] 1.3 Publicar página inicial e política de privacidade em URLs públicas, exigidas pelo Google para publicar o app: repositório público `sabortech/vettech-site` no GitHub Pages (`index.html`, `privacidade.html`), com a política baseada nos dados realmente tratados pelo Vet Tech e no uso limitado dos dados do Google.
- [ ] 1.4 Preencher o Branding no Google Auth Platform (nome, e-mail de suporte, página inicial, política de privacidade e domínio autorizado `sabortech.github.io`) e publicar o app ("Em produção"), dispensando a lista de usuários de teste; confirmar um login com conta Google fora da lista.

## 2. Backend Xano

- [x] 2.1 Criar em `xano/table/` as tabelas `tentativa_oauth_google` (hash do state, code_verifier interno, expiração), `vinculo_google` (sub único, perfil + identidade_id com par único, e-mail no vínculo, datas) e `uso_oauth_google` (marcador de uso único com chave única), todas não autenticáveis e com campos internos; verificar os índices únicos no workspace.
- [x] 2.2 Implementar `GET acesso/google/inicio` no grupo Authentication, com state aleatório, PKCE S256, expiração de 10 min e `redirect_uri` lido do ambiente; testar que a resposta contém somente a URL e que o state persiste apenas como hash.
- [x] 2.3 Implementar `POST acesso/google/retorno`: consumo único do state antes da troca do código, troca com segredo e verificador, validação de `iss`, `aud`, `exp`, `sub` e `email_verified`; `sub` vinculado → token igual ao de `acesso/login`; `sub` sem vínculo com identidade única e coerente → cria o vínculo (índices únicos arbitram conflito e concorrência) e emite o mesmo token, sem pedir senha.
- [x] 2.4 Remover do repositório e do workspace o que restou da etapa de senha descartada: endpoint `acesso/google/confirmar` e tabela `confirmacao_vinculo_google`.
- [x] 2.5 Testar os casos negativos: state ausente, repetido, expirado ou de outra tentativa; `error` do Google; e-mail não verificado; e-mail sem conta; e-mail nos dois perfis; reserva divergente; identidade já vinculada a outro `sub`; `sub` vinculado a identidade removida. Todos sem token, sem vínculo e com mensagem genérica, sem tokens Google ou e-mails em log.
- [x] 2.6 Provar o isolamento: token emitido via Google (primeiro acesso e acesso seguinte) para veterinário é negado em endpoints de tutor (e o inverso), e `tutor/me`/`veterinario/me` aceitam o token do perfil correto.

## 3. Frontend Reflex

- [x] 3.1 Adicionar a leitura de `GOOGLE_LOGIN_ENABLED` em `shared/config.py` (padrão desligado) e incluir as novas mensagens genéricas na lista segura de `shared/xano_client.py`.
- [x] 3.2 Extrair de `State.login` a rotina de publicação de sessão (confirmação em `{perfil}/me`, geração, carga de espécies e pets) para reutilizá-la no caminho Google sem duplicação; executar os testes unitários existentes de login.
- [x] 3.3 Implementar `start_google_login` (chama `inicio`, guarda o state na sessão da aba, redireciona) e `finish_google_login` (compara o state, limpa-o, chama `retorno`, publica a sessão); remover a etapa de senha (`confirm_google_link`, `cancel_google_link`); cobrir com testes unitários: state divergente/ausente, `error` na query, resposta atrasada após logout, falha do Xano, conta sem cadastro, sucesso para tutor e veterinário sem senha.
- [x] 3.4 Tornar o botão de `components/auth.py` acionável e acessível quando a flag estiver ligada (desabilitado durante envio) e inerte quando desligada; página `/login/google` em `pages/` só com carregamento e redirecionamento, usando o mesmo cartão com LED e as imagens otimizadas do login, registrada em `vet_tech.py`; compilar conforme a skill de processos Reflex.

## 4. Verificação conjunta e implantação

- [x] 4.1 Percorrer no navegador com usuários de teste Google: tutor e veterinário existentes (primeiro acesso cria o vínculo sem senha; segundo acesso entra pelo `sub`), e-mail sem conta (orientação de cadastro), cancelamento no Google, flag desligada; desktop e celular sem overflow. Registrar em `verification.md` sem dados pessoais.
- [x] 4.2 Confirmar a regressão do login por e-mail e senha, do cadastro e do logout; verificar que nenhum registro foi criado em `user`, `tutor` ou `veterinario` pelo fluxo Google.
- [ ] 4.3 Atualizar `docs/architecture.md` (fluxo OAuth no Xano, vínculo automático por e-mail verificado e rota de retorno) e documentar as variáveis — feito; ao hospedar o Reflex, adicionar a URI de produção ao cliente OAuth, resolver a URI única do Xano (design, seção 6), apontar o Branding para o domínio do app e só então habilitar a flag em produção, registrando o rollback (desligar a flag).
