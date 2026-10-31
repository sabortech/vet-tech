## MODIFIED Requirements

### Requirement: Presença global e assets resilientes
O sistema SHALL mostrar uma única tartaruga flutuante no canto inferior direito em todas as páginas, inclusive após navegação, com tamanho aproximado de 160 px desktop e menor no mobile, offsets de aproximadamente 24 px, safe area e área clicável restrita ao botão. O sistema SHALL preservar acesso às ações existentes e oferecer fallback quando assets faltarem.

#### Scenario: Navegar entre páginas
- **WHEN** uma pessoa acessa qualquer rota e navega para outra
- **THEN** uma única mascote permanece disponível no canto inferior direito sem bloquear permanentemente ações existentes

#### Scenario: Imagem indisponível
- **WHEN** uma camada transparente não pode ser carregada
- **THEN** um fallback simples mantém o botão visível e utilizável sem quebrar a página

### Requirement: Animação idle exclusivamente local
O sistema SHALL acompanhar o cursor suavemente com a imagem inteira até aproximadamente 4 px e 4 graus, com origem nos pés, preservando a proporção da tartaruga. Enquanto usar idle único, não SHALL deformar partes do bitmap para simular cabeça, olhos, piscada ou respiração. Movimento SHALL executar exclusivamente no navegador, sem eventos de mouse enviados ao backend, sem reler geometria a cada frame e sem loop contínuo após estabilizar. SHALL pausar em aba oculta.

#### Scenario: Movimento e repouso
- **WHEN** o cursor se move e depois para fora da mascote
- **THEN** a imagem inteira converge suavemente, o loop de rastreamento para e nenhuma chamada ao backend ocorre por esse movimento

#### Scenario: Aba oculta
- **WHEN** o documento fica oculto
- **THEN** o rastreamento e temporizadores de animação pausam até o retorno

### Requirement: Pose feliz e iluminação
O sistema SHALL trocar as camadas idle por tartaruga feliz de braços em V em hover, foco visível e pressionamento por toque, com crossfade de aproximadamente 150 ms e pop de escala. SHALL pausar rastreamento durante essa interação. Glow verde #39ff88 SHALL pulsar suavemente atrás da mascote; opção RGB SHALL alterar lentamente apenas a cor do glow.

#### Scenario: Hover ou foco
- **WHEN** o botão recebe hover ou foco de teclado
- **THEN** a pose feliz e glow aparecem, idle desaparece quando hover está disponível e rastreamento pausa


#### Scenario: Hover indisponível
- **WHEN** a imagem hover falta ou falha ao carregar
- **THEN** idle permanece visível e interação mantém apenas glow e pop

### Requirement: Acessibilidade e preferências de movimento
O botão SHALL ser acessível por teclado, ter nome “Abrir assistente Vet Tech”, não permitir drag ou seleção e funcionar em toque sem rastreamento. Com preferência de movimento reduzido, SHALL desativar rastreamento, respiração, piscadas, pop e pulso, preservando troca estática das poses.

#### Scenario: Movimento reduzido
- **WHEN** prefers-reduced-motion está ativo, inclusive se alterado durante uso
- **THEN** o botão mantém apenas a troca estática idle/hover e continua ativável

#### Scenario: Dispositivo de toque
- **WHEN** a pessoa toca e pressiona a mascote
- **THEN** a pose feliz aparece enquanto pressiona, sem seguir coordenadas de toque

### Requirement: Gancho público de clique sem chat
Ao ser ativado por mouse, teclado ou toque, o botão SHALL disparar uma única ocorrência de `window.dispatchEvent(new CustomEvent("vettech:mascote-click"))`, sem abrir interface ou fazer chamada ao backend.

#### Scenario: Ativação
- **WHEN** uma pessoa clica ou ativa com Enter ou Espaço
- **THEN** o evento público é disparado uma vez por ativação e nenhum chat é aberto


## ADDED Requirements

### Requirement: Proporção fiel e fundo completo
O sistema SHALL usar idle quadrado transparente com uma única tartaruga inteira sem sombra incorporada, sem esticar ou estreitar a arte. SHALL desenhar sombra elíptica suave sob os pés por CSS. O fundo do login SHALL cobrir toda a viewport, inclusive a faixa inferior da mascote, sem alterar os fundos das outras telas.

#### Scenario: Redimensionar a janela
- **WHEN** a viewport muda entre desktop e mobile
- **THEN** a imagem mantém sua proporção e o fundo de login não deixa faixa descoberta
