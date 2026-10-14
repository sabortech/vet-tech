# Design

## Context

Consulte `proposal.md` para a motivação e `specs/login-screen-presentation/spec.md` para os contratos visuais e de compatibilidade. A view funcional de login já existe em `vet_tech/components/auth.py`, é exibida nas rotas compostas em `vet_tech/pages/index.py` e envia os dados para `State.login` em `vet_tech/features/auth/state.py`. Esse estado autentica tutores usando e-mail e senha pelo endpoint `tutor/login`.

A tela de cadastro em `vet_tech/pages/cadastro.py` já estabelece padrões de apresentação Reflex, Nunito, tons de verde e o logotipo. O asset `assets/fundo02.jpeg` corresponde ao fundo florestal do protótipo. O cadastro e o login têm comportamentos separados; esta mudança não deve conectar os controles visuais ainda sem implementação.

## Goals / Non-Goals

**Goals:**

- Aproximar a composição da view de login do protótipo fornecido, mantendo o formulário existente conectado ao estado atual.
- Reaproveitar fonte, logotipo e imagem já disponíveis, evitando dependências novas e duplicação de lógica de autenticação.
- Tornar o layout adaptável a telas menores e manter os controles funcionais utilizáveis.

**Non-Goals:**

- Alterar a API, autenticação, validação, armazenamento de sessão ou suporte a login por CPF.
- Implementar lembrar sessão, recuperação de senha ou autenticação Google.
- Alterar a tela de cadastro, o perfil do tutor ou as rotas existentes.

## Decisões

### Manter a view e os eventos funcionais existentes

Aplicar a composição visual na view de login existente em `vet_tech/components/auth.py`, mantendo `on_submit=State.login`, os nomes dos campos enviados e os controles de estado/mensagem já usados. Isso limita a mudança à apresentação e evita criar uma segunda tela de login ou duplicar o fluxo.

Alternativa considerada: criar uma nova página ou estado de autenticação para reproduzir o protótipo. Rejeitada por aumentar o risco de divergência e contrariar o escopo estritamente visual.

### Compor o painel dividido usando recursos do projeto

Usar um cartão arredondado horizontal com painel claro para marca e formulário e painel lateral preenchido por `assets/fundo02.jpeg`, aplicando recorte `cover`. O conteúdo do painel claro segue a hierarquia do protótipo: mascote/logo, nome Vet Tech, mensagem de boas-vindas, campos, linha de opções, botão principal, divisor, apresentação Google e chamada para cadastro. Reutilizar Nunito e a paleta de verdes já aplicada no cadastro. Em telas estreitas, reorganizar ou ocultar apenas a imagem decorativa para conservar a área de formulário.

Alternativa considerada: carregar imagens remotas ou adicionar novo recurso visual. Rejeitada porque o asset correspondente já está no projeto e não há necessidade de dependência externa.

### Exibir elementos sem criar novos fluxos

Preservar a hierarquia visual dos itens de lembrar acesso, recuperação e Google conforme o protótipo, mas não adicionar handlers ou conexões de backend para eles. O link de cadastro pode manter somente a navegação já existente. O texto “E-mail ou CPF” pode ser exibido por fidelidade visual, mas o campo continua associado ao valor de e-mail usado por `State.login`; CPF não se torna um identificador de autenticação.

Alternativa considerada: implementar ou conectar esses fluxos junto com a estilização. Rejeitada porque ultrapassa o escopo confirmado pelo usuário.

## Risks / Trade-offs

- **[Risco]** A apresentação de “E-mail ou CPF”, recuperação, lembrar acesso ou Google pode ser interpretada como funcionalidade disponível → **Mitigação:** não alterar o comportamento atual, não adicionar ações falsas e manter explícito que CPF, persistência de sessão, recuperação e Google estão fora desta mudança.
- **[Risco]** O painel de imagem consumir espaço ou tornar o formulário estreito em dispositivos menores → **Mitigação:** usar composição responsiva e ocultar ou reposicionar somente o conteúdo decorativo.
- **[Risco]** A composição visual divergira em excesso do cadastro existente → **Mitigação:** reutilizar a identidade, os recursos e os padrões Reflex presentes, sem reestruturar outras páginas.

## Plano de migração

Não há alteração de dados, backend ou dependências. A implantação consiste em atualizar a apresentação da tela existente. Para rollback, restaurar a composição visual anterior da view, mantendo intacto o fluxo funcional de autenticação.
