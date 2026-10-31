## MODIFIED Requirements

### Requirement: Presença global e assets resilientes
O sistema SHALL mostrar uma única tartaruga flutuante no canto inferior direito em todas as páginas, inclusive após navegação, com tamanho aproximado de 140 px desktop e menor no mobile, offsets de aproximadamente 24 px, safe area e área clicável restrita ao botão. O botão SHALL flutuar sobre a página sem faixa reservada, scrollport próprio, redução da viewport ou deslocamento do conteúdo. O sistema SHALL preservar acesso às ações existentes e oferecer fallback quando assets faltarem.

#### Scenario: Navegar entre páginas
- **WHEN** uma pessoa acessa qualquer rota e navega para outra
- **THEN** uma única mascote permanece disponível no canto inferior direito sem bloquear permanentemente ações existentes

#### Scenario: Imagem indisponível
- **WHEN** uma camada transparente não pode ser carregada
- **THEN** um fallback simples mantém o botão visível e utilizável sem quebrar a página


#### Scenario: Geometria independente da mascote
- **WHEN** a mascote é renderizada ou temporariamente ocultada para comparação
- **THEN** tamanho e posição do conteúdo e altura do documento permanecem iguais

### Requirement: Pose feliz e iluminação
O sistema SHALL trocar as camadas idle por tartaruga feliz de braços em V em hover, foco visível e pressionamento por toque, com crossfade de aproximadamente 150 ms e pop de escala. SHALL pausar rastreamento durante essa interação. Glow verde #39ff88 SHALL emitir duas piscadas lentas e suaves em aproximadamente 4 segundos e permanecer aceso com intensidade estável enquanto houver hover ou foco; ao sair SHALL apagar e na próxima entrada SHALL reiniciar; opção RGB SHALL alterar lentamente apenas a cor do glow.

#### Scenario: Hover ou foco
- **WHEN** o botão recebe hover ou foco de teclado
- **THEN** a pose feliz e glow aparecem, idle desaparece quando hover está disponível e rastreamento pausa


#### Scenario: Hover indisponível
- **WHEN** a imagem hover falta ou falha ao carregar
- **THEN** idle permanece visível e interação mantém apenas glow e pop

#### Scenario: Duas piscadas e LED constante
- **WHEN** a pessoa mantém hover ou foco visível por mais de quatro segundos
- **THEN** o glow completa duas pulsações suaves e permanece aceso sem pulsação contínua

#### Scenario: Nova interação
- **WHEN** a pessoa sai da mascote e depois volta
- **THEN** o glow apaga na saída e reinicia a sequência de duas piscadas na entrada
