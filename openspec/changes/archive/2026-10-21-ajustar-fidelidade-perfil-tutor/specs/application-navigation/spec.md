# Spec Delta

## MODIFIED Requirements

### Requirement: Navegação lateral reutilizável e com área ativa identificável
O sistema SHALL apresentar nas áreas autenticadas uma navegação lateral compartilhada com a marca Vet Tech e as opções Dashboard, Prontuário, Vacinas, Consultas, Exames, Meus Pets e Configurações. A opção correspondente à área atual SHALL ser identificada visualmente como ativa e a patinha da marca SHALL usar a mesma cor do texto “Vet Tech”. No modo expandido, os itens SHALL ter área de interação de aproximadamente 48 px de altura e o item ativo SHALL manter o destaque branco com cantos arredondados.

#### Scenario: Perfil do tutor identifica Meus Pets como área ativa
- **WHEN** o tutor autenticado visualiza o perfil atual
- **THEN** a opção “Meus Pets” aparece ativa e as demais opções permanecem visíveis

#### Scenario: Navegação usada em outra área autenticada
- **WHEN** outra tela autenticada integra a navegação compartilhada e informa sua área atual
- **THEN** a mesma navegação é apresentada com essa área ativa, sem duplicar sua composição visual

#### Scenario: Marca mantém proporção e cor consistentes
- **WHEN** a sidebar aparece em modo expandido ou recolhido
- **THEN** a patinha e o texto “Vet Tech” usam o mesmo token de cor e a marca e os itens permanecem alinhados sem cortes

### Requirement: Navegação lateral adapta-se a desktop e dispositivos móveis
O sistema SHALL manter sempre visível um controle acessível para alternar a navegação. Em desktop, SHALL permitir alternar entre modo expandido de aproximadamente 260 px e rail de aproximadamente 72–80 px, usando transição suave e redimensionando a área de conteúdo restante sem sobreposição ou rolagem horizontal. A adaptação do conteúdo SHALL considerar o espaço disponível após a sidebar, e não somente a largura total da viewport. Em viewports abaixo de 768 px, SHALL apresentar a navegação como drawer sobreposto, fechado por padrão, com backdrop que fecha o drawer quando acionado.

#### Scenario: Alternância da navegação em desktop
- **WHEN** o tutor alterna o controle de navegação em viewport desktop
- **THEN** o menu muda suavemente entre largura expandida e rail, e o conteúdo usa o espaço restante sem sobreposição ou rolagem horizontal

#### Scenario: Itens do rail recolhido ficam centralizados
- **WHEN** a sidebar está recolhida em desktop
- **THEN** os ícones dos sete itens ficam centralizados no eixo vertical da sidebar, alinhados com a patinha da marca e o botão de alternar
- **AND** os rótulos ficam ocultos sem espaço residual, o item ativo mantém o ícone no centro do pill e cada item mantém tooltip com seu nome
- **AND** os itens permanecem alinhados à esquerda com ícone e texto quando a sidebar está aberta

#### Scenario: Ícone e nome acessível do toggle refletem o estado desktop
- **WHEN** a sidebar está recolhida
- **THEN** o botão mostra o ícone de menu e expõe o nome acessível “Abrir menu” com `aria-expanded` falso
- **WHEN** a sidebar está aberta
- **THEN** o botão mostra um ícone de recolher apontando à esquerda e expõe o nome acessível “Recolher menu” com `aria-expanded` verdadeiro

#### Scenario: Layout se adapta à largura restante
- **WHEN** o estado expandido da sidebar reduz a área disponível para a tela autenticada
- **THEN** o conteúdo reorganiza suas colunas de acordo com a largura restante, sem comprimir cartões ou campos abaixo de uma largura legível

#### Scenario: Abertura e fechamento do drawer móvel
- **WHEN** o tutor abre o controle de navegação em viewport abaixo de 768 px
- **THEN** o drawer é exibido sobre o conteúdo com backdrop e o conteúdo continua ocupando a largura disponível
- **AND** acionar o backdrop ou pressionar Esc fecha o drawer
