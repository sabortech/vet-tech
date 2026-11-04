# Preferências de interface

## Purpose

Permitir que a pessoa escolha o tema da interface inteira e a expansão do menu, com aplicação imediata e persistência local sem armazenar informações pessoais da conta.

## Requirements

### Requirement: Preferências oferecem aparência e navegação
O sistema SHALL apresentar na aba Preferências um cartão Aparência com o controle Modo escuro e um cartão Navegação com Manter o menu lateral expandido. Ambos SHALL usar o mesmo estilo de switch, com dimensões, cores e foco consistentes, e refletir o estado efetivo e aplicar alterações imediatamente, sem botão de salvamento, com descrição de persistência neste navegador.

#### Scenario: Alternância de preferência
- **WHEN** o tutor altera um dos controles
- **THEN** a interface reflete a escolha imediatamente e apresenta confirmação discreta sem depender da API Xano

### Requirement: Tema é coerente em todo o sistema
O sistema SHALL oferecer claro e escuro para Configurações, Meus Pets, login e cadastro, incluindo a cor da sidebar, cartões, campos, seletores, mensagens, diálogos, chat flutuante global e estados de foco e desabilitado. SHALL preservar Nunito, hierarquia, dimensões e identidade verde. Login e cadastro SHALL seguir a preferência de tema, preservando sua estrutura, imagens e identidade visual.

#### Scenario: Navegação no modo escuro
- **WHEN** o tutor ativa Modo escuro e navega entre Configurações e Meus Pets
- **THEN** ambas as telas usam o mesmo tema, sem superfícies claras residuais ou texto ilegível

#### Scenario: Saída da área autenticada
- **WHEN** a sessão termina e a pessoa visualiza login ou cadastro
- **THEN** essas telas continuam usando o tema escolhido e preservam sua estrutura e identidade visual

#### Scenario: Chat acompanha a preferência em todos os perfis
- **WHEN** visitante, tutor ou veterinário abre o assistente com tema claro ou escuro, ou a preferência muda enquanto o chat está aberto
- **THEN** painel, mensagens, campo de texto, ações e histórico acompanham imediatamente a mesma preferência sem reiniciar a conversa

### Requirement: Preferências são locais e carregam sem flash de tema incorreto
O sistema SHALL lembrar tema e expansão neste navegador, sem gravar token, dados pessoais ou senhas nesse mecanismo. Sem preferência de tema válida SHALL usar claro; sem preferência válida de expansão SHALL manter o padrão expandido. O tema salvo SHALL ser aplicado antes da apresentação visível de qualquer tela, sem mostrar brevemente o tema oposto. Se o armazenamento estiver indisponível, a interface SHALL continuar utilizável com preferência em memória durante a página atual.

#### Scenario: Preferência salva é retomada
- **GIVEN** há preferência escura salva neste navegador
- **WHEN** qualquer tela é apresentada novamente
- **THEN** seu primeiro conteúdo visível já usa o tema escuro
- **AND** a preferência não cria nem restaura uma sessão autenticada

#### Scenario: Armazenamento indisponível ou valor inválido
- **WHEN** o armazenamento local não pode ser usado ou contém valor desconhecido
- **THEN** a tela permanece utilizável, usa o padrão no caso de valor inválido e não promete sincronização entre dispositivos

### Requirement: Preferência do menu reutiliza o estado compartilhado
O controle de expansão SHALL compartilhar o estado existente com o botão da sidebar e manter a escolha entre páginas e abas do mesmo navegador. Em celular, SHALL preservar o comportamento atual de gaveta fechada por padrão, independentemente da preferência desktop.

#### Scenario: Controle e sidebar sincronizados
- **WHEN** o tutor recolhe ou expande a sidebar por qualquer um dos dois controles
- **THEN** o outro controle reflete o mesmo estado sem preferência concorrente

#### Scenario: Celular preserva gaveta
- **GIVEN** há preferência desktop expandida
- **WHEN** a tela é usada abaixo de 768 px
- **THEN** o menu continua em gaveta inicialmente fechada e pode ser aberto e fechado normalmente

### Requirement: Borda luminosa global do assistente
O sistema SHALL apresentar um segmento verde luminoso com halo percorrendo suavemente um caminho em oito na janela aberta do assistente. O percurso SHALL alternar as voltas do cabeçalho/banner e das mensagens/rodapé, compartilhando a divisória entre banner e mensagens sem diagonais sobre conteúdo. SHALL manter ciclo linear contínuo de 6s, ou 12s em movimento reduzido. O efeito SHALL funcionar para visitantes, tutores e veterinários, nos dois temas e em desktop/celular, adaptando-se ao tamanho real do banner. SHALL NOT interceptar cliques, foco, mensagens ou histórico. Ao fechar/minimizar SHALL deixar de animar.

#### Scenario: Abrir em qualquer perfil
- **WHEN** visitante, tutor ou veterinário abre o assistente em uma tela disponível
- **THEN** o mesmo efeito percorre as duas voltas e a divisória, e os controles da conversa continuam funcionais

#### Scenario: Tema e tamanho da janela
- **WHEN** o tema muda ou o chat é aberto no celular
- **THEN** o traço mantém o movimento e acompanha o perímetro e a divisória sem cobrir conteúdo nem criar overflow

#### Scenario: Minimizar e reabrir
- **WHEN** o chat é minimizado e reaberto
- **THEN** o efeito para enquanto fechado e volta a circular quando a janela é exibida

#### Scenario: Percorrer a divisória
- **WHEN** o chat está aberto
- **THEN** o segmento alterna as duas voltas e passa pela linha divisória inferior do banner durante o ciclo contínuo, sem saltos de posição

#### Scenario: Redimensionar o chat
- **WHEN** a janela ou altura do banner muda
- **THEN** o caminho mantém as curvas externas e a passagem pela divisória real sem invadir texto e controles

#### Scenario: Tema e movimento reduzido
- **WHEN** o usuário alterna o tema ou solicita movimento reduzido
- **THEN** o halo acompanha o segmento nos dois temas e a circulação continua em 12s quando o movimento é reduzido

### Requirement: Texto legível em todo o sistema no tema claro
O sistema SHALL apresentar textos principais verde quase preto, textos secundários cinza escuro e links verdes escuros sobre superfícies claras em todas as telas públicas, áreas de tutor e veterinário, formulários, tabelas, mensagens, menus e diálogos. Textos comuns habilitados SHALL ter contraste mínimo de 4,5:1 sobre seu fundo; textos grandes SHALL ter pelo menos 3:1. Botões e sidebar SHALL manter texto legível em seus fundos coloridos. A preferência de tema do projeto SHALL controlar também os componentes padrão e portais, mesmo quando houver preferência conflitante do framework, preservando legibilidade no tema escuro.

#### Scenario: Conteúdo e controles claros
- **WHEN** a pessoa visualiza qualquer tela ou abre um menu ou diálogo no tema claro
- **THEN** os textos e valores dos campos usam cores escuras e legíveis nas superfícies claras, preservando a hierarquia visual

#### Scenario: Preferência conflitante e alternância
- **GIVEN** o framework possui preferência escura e o projeto possui preferência clara
- **WHEN** a página carrega ou a pessoa alterna o tema
- **THEN** componentes padrão, conteúdo e portais acompanham o tema escolhido no projeto sem texto claro sobre fundo branco

### Requirement: Ícone do mascote em todas as páginas
O sistema SHALL apresentar o rosto do mascote como ícone da aba em todas as páginas públicas e autenticadas, preservando enquadramento reconhecível em 16px/32px e o mesmo ícone ao navegar entre rotas. SHALL manter fallback PNG e preferência claro/escuro sem exibir o ícone padrão do Reflex.

#### Scenario: Abrir e navegar por páginas
- **WHEN** qualquer página do sistema é apresentada ou a pessoa navega para outra rota
- **THEN** a aba usa o ícone global do mascote com rosto em destaque

### Requirement: Comandos com cantos arredondados no sistema
O sistema SHALL apresentar cantos arredondados nos botões de todas as páginas e painéis, incluindo botões nativos, Radix e links com aparência de botão, preservando foco, estados, cliques e os formatos próprios de controles de seleção.

#### Scenario: Usar comandos em qualquer página
- **WHEN** a pessoa visualiza comandos no sistema nos temas claro ou escuro
- **THEN** os botões possuem cantos arredondados sem mudar sua ação
