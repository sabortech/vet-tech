# Design

## Context

Ver `proposal.md` para a motivação. A inspeção encontrou duas composições de menu do tutor:

| Implementação atual | Uso | Situação visual |
| --- | --- | --- |
| `components/sidebar.py` e `.sidebar-*` em `assets/vet_tech.css` | Meus Pets e Configurações | Design personalizado: verde, marca com patinha, pill ativo branco, tokens de tema, rail e drawer |
| `components/navigation.py::sidebar` | `pages/profile.py::tutor_area` no Prontuário | Layout paralelo com `rx.button`, fundo de superfície e medidas inline; não aplica o acabamento da sidebar personalizada |

O segundo menu tem estilo, mas é principalmente o padrão dos componentes Reflex: “sem design” significa sem aplicar o design personalizado já existente. A área veterinária possui uma terceira composição, fora do escopo.

Ambos leem `NavigationState.sidebar_expanded`, porém o Prontuário usa esse estado desktop para controlar uma sobreposição móvel. O menu personalizado já separa `drawer_open`. A preferência persistente é `vet_tech_sidebar_expanded`; não criar outra.

`assets/preferences.js` intercepta links `.sidebar a.sidebar-item` quando há edição pendente. O controle oculto em Configurações solicita sempre `/`, e `SettingsState.request_action` ainda não aceita destinos clínicos. A unificação precisa corrigir esse desvio. `State.set_pet_modal` também retorna um redirect para `/login`; preservar a rota exige retirar esse efeito ao abrir/fechar o modal clínico.

As specs atuais divergem: `application-navigation` descreve sete entradas globais e `authenticated-navigation` descreve cinco seções clínicas. Os dois deltas desta change reconciliam os contratos, sem tratar nenhuma das duas listas como a única funcionalidade válida.

## Goals / Non-Goals

**Goals:** uma composição visual, catálogo de itens centralizado, intenção de navegação explícita e comportamento responsivo uniforme no tutor, mantendo eventos e dados da sessão existentes.

**Non-Goals:** redesenhar o conteúdo clínico, mover módulos indiscriminadamente, criar rotas de Dashboard/Exames, unificar o menu veterinário ou alterar contratos de autorização e persistência.

## Decisions

### 1. Reutilizar a sidebar personalizada como composição única

Evoluir `components/sidebar.py::layout_com_menu` para aceitar área/seção ativa e um slot de ações clínicas. `tutor_area` passa a usar esse layout; retirar sua sidebar paralela, margens compensatórias, backdrop e controle móvel próprios. `components/navigation.py` pode conservar apenas a composição do modal/ações, sem renderizar outro menu. Evitar um import circular: sidebar não deve importar `pets` ou o estado de configurações; receber conteúdo ou handlers pelas páginas que já conhecem esses módulos.

Copiar CSS para o menu padrão foi descartado porque preservaria duas árvores com estados e semânticas divergentes. O catálogo global fica em um só lugar, com nove entradas na ordem de `proposal.md`; Dashboard/Exames continuam desabilitados. Novo pet/Mudar pet/Sair são ações contextualizadas no Prontuário, com classes compatíveis, sem obrigar a mover o formulário permanente de Meus Pets.

### 2. Separar destino de rota e seção clínica

Rotas existentes permanecem `/`, `/configuracoes` e `/prontuario`. Links clínicos apontam a `/prontuario?secao=<chave>`, com allowlist: `inicio`, `vacinas`, `medicamentos`, `doencas`, `consultas`. Sem parâmetro, Prontuário abre Início. Não inserir token ou pet na URL.

Um evento curto de entrada aplica a seção validada e delega somente ao carregamento já existente, respeitando cache, deduplicação e seleção explícita. Se o pet ainda não estiver escolhido, manter a intenção da seção até a seleção terminar. Parâmetro inválido usa Início. Atualizar o parâmetro entre seções da mesma rota precisa disparar a aplicação da intenção; verificar navegação e voltar/avançar no navegador, sem depender apenas de `on_mount`.

Resolver o ativo pelo destino: Meus Pets e Configurações usam suas rotas; no Prontuário, Início ativa Prontuário e as demais seções ativam seu próprio item. Um só item recebe `aria-current="page"`. Links limpos continuam usando o router do navegador sem esperar Xano.

### 3. Drawer móvel separado da preferência desktop

Reutilizar `NavigationState.drawer_open`, toolbar e backdrop atuais, com o breakpoint de 768 px do CSS personalizado. A expansão desktop continua persistida em LocalStorage; drawer é transitório e não abre por causa dessa preferência. Fechar por Esc/backdrop e após aplicar uma navegação. No descarte cancelado, não executar o destino e restaurar foco adequadamente. Preservar foco visível e nomes acessíveis no rail.

### 4. Guard com intenção exata e allowlist

Estender o guard para transportar o destino efetivamente clicado, incluindo `secao`, usando uma allowlist das rotas e seções conhecidas no servidor. O mecanismo pode usar controles ocultos por destino autorizado ou um evento com valor validado; não aceitar redirecionamento arbitrário de URL. Durante uma gravação, manter o bloqueio atual. Com formulário limpo, o link permanece navegação direta.

As ações Sair e a navegação para seções clínicas respeitam a confirmação existente de Configurações. A preferência de tema/expansão e o fechamento do drawer não são abandono de formulário e não exigem descarte.

### 5. Preservar ações e carregamento clínico

O modal Novo pet usa o handler existente de abertura/fechamento e limpeza do formulário, sem redirect para `/login` e sem criar outra sessão. Mudar pet continua limpando o contexto e invalidando cargas antigas. Sair mantém o logout existente.

Não disparar Xano ao montar ou recolher a sidebar. A seleção/carregamento permanece sob a State clínica e a capacidade `pet-clinical-loading`: reutilização por 60 segundos, spinner e leituras em background. Não adicionar um estado paralelo de pet no menu.

## Risks / Trade-offs

- [Nove entradas e ações ultrapassarem a altura disponível] → região rolável do menu com ações alcançáveis, testada em 390×844 e com zoom, sem comprimir os alvos.
- [Link clínico perder a seção ao navegar ou escolher pet] → allowlist única e testes para mesma rota, outra rota, sem pet e voltar/avançar.
- [Mudança do guard perder edição ou encaminhar ao destino errado] → testar continuar/descarte em todos os destinos, incluindo query string, e bloqueio durante gravação.
- [CSS do contexto clínico sobrescrever o menu] → usar as classes e tokens existentes, comparar screenshots e medidas nos temas claro/escuro e nos modos expandido/rail.
- [Novos imports criarem ciclo sidebar → pets → sidebar] → composição por slots, sem mover estado de negócio para componentes.
- [Alteração de aparência causar regressão de desempenho] → adaptar `pet_loading_browser.py` e verificar que menu e navegação não aumentam chamadas clínicas nem bloqueiam durante HTTP.

## Migration Plan

1. Registrar referências do menu personalizado e a matriz de navegação atual; implementar catálogo e composição compartilhados com testes dos destinos.
2. Integrar Prontuário, ações, drawer e guard, preservando páginas e contratos existentes.
3. Executar testes de navegação/configurações/contexto clínico, `reflex compile --dry` e navegador em claro/escuro, desktop/celular e rail, com evidências sanitizadas.
4. Atualizar a documentação de navegação e reiniciar o Reflex para validar a composição compilada. Rollback reverte a aplicação, sem migração de banco ou alteração dos dados do pet.
