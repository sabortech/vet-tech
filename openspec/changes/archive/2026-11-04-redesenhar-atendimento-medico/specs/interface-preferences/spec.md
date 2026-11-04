## MODIFIED Requirements

### Requirement: Borda luminosa global do assistente
O sistema SHALL apresentar um segmento verde luminoso com halo percorrendo suavemente um caminho em oito na janela aberta do assistente. O percurso SHALL alternar as voltas do cabeçalho/banner e das mensagens/rodapé, compartilhando a divisória entre banner e mensagens sem diagonais sobre conteúdo. SHALL manter ciclo linear contínuo de 6s, ou 12s em movimento reduzido. O efeito SHALL funcionar para visitantes, tutores e veterinários, nos dois temas e em desktop/celular, adaptando-se ao tamanho real do banner. SHALL NOT interceptar cliques, foco, mensagens ou histórico. Ao fechar/minimizar SHALL deixar de animar.

#### Scenario: Percorrer a divisória
- **WHEN** o chat está aberto
- **THEN** o segmento alterna as duas voltas e passa pela linha divisória inferior do banner durante o ciclo contínuo, sem saltos de posição

#### Scenario: Redimensionar o chat
- **WHEN** a janela ou altura do banner muda
- **THEN** o caminho mantém as curvas externas e a passagem pela divisória real sem invadir texto e controles

#### Scenario: Tema e movimento reduzido
- **WHEN** o usuário alterna o tema ou solicita movimento reduzido
- **THEN** o halo acompanha o segmento nos dois temas e a circulação continua em 12s quando o movimento é reduzido

#### Scenario: Abrir em qualquer perfil
- **WHEN** visitante, tutor ou veterinário abre o assistente em uma tela disponível
- **THEN** o mesmo efeito percorre as duas voltas e a divisória, e os controles da conversa continuam funcionais

#### Scenario: Tema e tamanho da janela
- **WHEN** o tema muda ou o chat é aberto no celular
- **THEN** o traço mantém o movimento e acompanha o perímetro e a divisória sem cobrir conteúdo nem criar overflow

#### Scenario: Minimizar e reabrir
- **WHEN** o chat é minimizado e reaberto
- **THEN** o efeito para enquanto fechado e volta a circular quando a janela é exibida

## ADDED Requirements

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
