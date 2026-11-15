# Proposta

## Why

A tela de login já exibe "Entrar com Google" apenas como elemento visual do protótipo, sem ação. Tutores e veterinários que usam conta Google precisam digitar e-mail e senha do Vet Tech em todo acesso. Permitir a entrada pelo Google reduz atrito sem abrir mão das regras de identidade já entregues: um perfil por e-mail, perfil derivado no backend e token isolado por entidade.

## What Changes

- Tornar funcional o botão "Entrar com Google" em `/login`, para **tutor e veterinário**, sem seletor de perfil: o backend resolve o perfil pela identidade já cadastrada, como no login por senha.
- Executar o fluxo OAuth 2.0 / OpenID Connect (código de autorização com PKCE e `state` de uso único) **no Xano**: geração da URL de autorização, troca do código com o segredo do cliente, validação das claims do Google, resolução da identidade, vínculo e emissão do token ficam no grupo Authentication. O Reflex apenas redireciona o navegador e repassa `code`/`state` recebidos na rota de retorno.
- **Somente contas existentes**: o Google não cria tutor nem veterinário. Se o e-mail Google não pertencer a nenhuma conta, a pessoa recebe orientação para usar o cadastro atual (CPF/CRMV continuam obrigatórios).
- **Sem senha do Vet Tech**: o login Google nunca pede a senha do Vet Tech, nem no primeiro acesso. No primeiro login, quando o Google informar `email_verified = true` e o e-mail normalizado corresponder a exatamente uma identidade e reserva coerentes, o backend grava automaticamente o vínculo do identificador Google (`sub`) com essa identidade e emite a sessão. Nos acessos seguintes, a resolução é pelo `sub` vinculado.
- Manter o login por e-mail e senha sem alteração; o Google é uma entrada adicional para a mesma identidade.
- Novas variáveis de ambiente no Xano (cliente OAuth) e uma no Reflex (habilitação do botão). Nenhum segredo no repositório ou no frontend.

Fora do escopo: cadastro de contas pelo Google, desvincular ou trocar a conta Google pela interface, outros provedores, login Google em contas com e-mail duplicado entre perfis, notificações por e-mail e alterações no fluxo de recuperação de senha (`acesso/password-reset/*`, presente no workspace Xano e ainda fora do repositório).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `profile-authentication`: entrada alternativa pelo Google para identidades existentes, vínculo automático por e-mail verificado e estável pelo `sub`, `state` de uso único e as mesmas garantias de isolamento de token e sessão.
- `login-screen-presentation`: o botão Google deixa de ser somente visual e passa a iniciar o fluxo quando habilitado, com rota de retorno e mensagens genéricas.

## Impact

- **Xano** (`xano/`): tabelas `vinculo_google`, `tentativa_oauth_google` e `uso_oauth_google`; endpoints `acesso/google/inicio` e `acesso/google/retorno` no grupo Authentication; funções `Identity/resolve_login_email`, `Identity/linked_identity_valid` e `Identity/issue_session`; variáveis de ambiente do workspace.
- **Reflex**: `features/auth/state.py` (eventos de início e retorno reutilizando a mesma verificação em `{perfil}/me` e a limpeza de sessão), `components/auth.py` (botão), nova página `/login/google` em `pages/` registrada em `vet_tech.py` (mesmo cartão com LED de `auth-decoration` e imagens otimizadas), `shared/config.py` (flag) e lista de mensagens seguras em `shared/xano_client.py`.
- **Dados pessoais e privacidade**: armazena o `sub` do Google e o e-mail informado no momento do vínculo, ambos internos e nunca devolvidos ao cliente. Não lê nem expõe prontuário, pets ou dados clínicos; não altera a autorização tutor → veterinário nem a auditoria de prontuário. O vínculo registra data de criação e último uso para rastreabilidade de acesso, sem persistir tokens do Google.
- **Segurança**: sem a senha, o acesso pelo Google depende de o Google ter verificado o e-mail; quem controla a conta Google de um e-mail cadastrado entra na conta Vet Tech correspondente. Risco aceito pela decisão de produto (ver design).
- **Autorização do tutor**: não exige nova verificação de autorização clínica; o token emitido é idêntico ao do login por senha e continua sujeito às mesmas regras de cada endpoint.
- **Notificações**: nenhuma nesta entrega. Avisar por e-mail sobre novo vínculo Google fica como melhoria futura.
- **Configuração externa**: cliente OAuth "Aplicativo da Web" no Google Cloud Console (um só cliente por enquanto, com a URI `http://localhost:3000/login/google`), tela de consentimento com escopos `openid email profile` e app publicado ("Em produção") para dispensar a lista de usuários de teste. A publicação exige página inicial e política de privacidade públicas, hospedadas no GitHub Pages em `sabortech/vettech-site`, já que o Vet Tech ainda roda só localmente.
