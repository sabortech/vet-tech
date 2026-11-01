## ADDED Requirements

### Requirement: Texto legível em todo o sistema no tema claro
O sistema SHALL apresentar textos principais verde quase preto, textos secundários cinza escuro e links verdes escuros sobre superfícies claras em todas as telas públicas, áreas de tutor e veterinário, formulários, tabelas, mensagens, menus e diálogos. Textos comuns habilitados SHALL ter contraste mínimo de 4,5:1 sobre seu fundo; textos grandes SHALL ter pelo menos 3:1. Botões e sidebar SHALL manter texto legível em seus fundos coloridos. A preferência de tema do projeto SHALL controlar também os componentes padrão e portais, mesmo quando houver preferência conflitante do framework, preservando legibilidade no tema escuro.

#### Scenario: Conteúdo e controles claros
- **WHEN** a pessoa visualiza qualquer tela ou abre um menu ou diálogo no tema claro
- **THEN** os textos e valores dos campos usam cores escuras e legíveis nas superfícies claras, preservando a hierarquia visual

#### Scenario: Preferência conflitante e alternância
- **GIVEN** o framework possui preferência escura e o projeto possui preferência clara
- **WHEN** a página carrega ou a pessoa alterna o tema
- **THEN** componentes padrão, conteúdo e portais acompanham o tema escolhido no projeto sem texto claro sobre fundo branco
