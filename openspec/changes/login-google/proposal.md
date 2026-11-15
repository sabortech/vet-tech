# Proposta

## Why

A tela de login já exibe "Entrar com Google" apenas como elemento visual do protótipo, sem ação. Tutores e veterinários que usam conta Google precisam digitar e-mail e senha do Vet Tech em todo acesso. Permitir a entrada pelo Google reduz atrito sem abrir mão das regras de identidade já entregues: um perfil por e-mail, perfil derivado no backend e token isolado por entidade.

## What Changes

- Tornar funcional o botão "Entrar com Google" em `/login`, para **tutor e veterinário**, sem seletor de perfil: o backend resolve o perfil pela identidade já cadastrada, como no login por senha.
- Executar o fluxo OAuth 2.0 / OpenID Connect (código de autorização com PKCE e `state` de uso único) **no Xano**: geração da URL de autorização, troca do código com o segredo do cliente, validação das claims do Google, resolução da identidade, vínculo e emissão do token ficam no grupo Authentication. O Reflex apenas redireciona o navegador, repassa `code`/`state` recebidos na rota de retorno e coleta a senha na confirmação do primeiro acesso.
- **Somente contas existentes**: o Google não cria tutor nem veterinário. Se o e-mail Google não pertencer a nenhuma conta, a pessoa recebe orientação para usar o cadastro atual (CPF/CRMV continuam obrigatórios).
- **Primeiro login exige a senha uma única vez**: quando o `sub` do Google ainda não tem vínculo e o e-mail verificado corresponde a exatamente uma identidade, o backend **não** vincula nem emite sessão. Ele registra uma confirmação pendente de uso único (10 min, tentativas limitadas), e a rota de retorno pede a senha do Vet Tech dessa conta, sem campo de e-mail editável. Só com a senha correta o backend grava o vínculo do `sub` com a identidade e emite o token. Nos acessos seguintes, a resolução é pelo `sub` vinculado, sem pedir senha.
- Manter o login por e-mail e senha sem alteração; o Google é uma entrada adicional para a mesma identidade.
- Novas variáveis de ambiente no Xano (cliente OAuth) e uma no Reflex (habilitação do botão). Nenhum segredo no repositório ou no frontend.

Fora do escopo: cadastro de contas pelo Google, desvincular ou trocar a conta Google pela interface, outros provedores, login Google em contas com e-mail duplicado entre perfis, notificações por e-mail e recuperação de senha (quem não lembra a senha continua sem conseguir concluir o primeiro vínculo até existir esse fluxo).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `profile-authentication`: entrada alternativa pelo Google para identidades existentes, vínculo confirmado por senha no primeiro acesso, `state` e confirmação de uso único e as mesmas garantias de isolamento de token e sessão.
- `login-screen-presentation`: o botão Google deixa de ser somente visual e passa a iniciar o fluxo quando habilitado, com rota de retorno, etapa de confirmação de senha no primeiro acesso e mensagens genéricas.

## Impact

- **Xano** (`xano/`): tabelas `vinculo_google`, `tentativa_oauth_google` e `confirmacao_vinculo_google`; endpoints `acesso/google/inicio`, `acesso/google/retorno` e `acesso/google/confirmar` no grupo Authentication; variáveis de ambiente do workspace. Publicação somente após verificação em ambiente de teste.
- **Reflex**: `features/auth/state.py` (eventos de início, retorno e confirmação reutilizando a mesma verificação em `{perfil}/me` e a limpeza de sessão), `components/auth.py` (botão), nova página `/login/google` em `pages/` registrada em `vet_tech.py` (mesmo cartão com LED de `auth-decoration` e imagens otimizadas), `shared/config.py` (flag) e lista de mensagens seguras em `shared/xano_client.py`.
- **Dados pessoais e privacidade**: armazena o `sub` do Google e o e-mail informado no momento do vínculo, ambos internos e nunca devolvidos ao cliente além do próprio e-mail Google exibido na confirmação. A confirmação pendente guarda `sub`, e-mail e identidade só até expirar ou ser usada. Não lê nem expõe prontuário, pets ou dados clínicos; não altera a autorização tutor → veterinário nem a auditoria de prontuário. O vínculo registra data de criação e último uso para rastreabilidade de acesso, sem persistir tokens do Google nem a senha digitada.
- **Autorização do tutor**: não exige nova verificação de autorização clínica; o token emitido é idêntico ao do login por senha e continua sujeito às mesmas regras de cada endpoint.
- **Notificações**: nenhuma nesta entrega. Avisar por e-mail sobre novo vínculo Google fica como melhoria futura.
- **Configuração externa**: cliente OAuth "Aplicativo da Web" no Google Cloud Console, com URI de redirecionamento do Reflex por ambiente e tela de consentimento com escopos `openid email profile`.
