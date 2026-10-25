# Spec Delta

## Purpose

Oferece navegação consistente entre as áreas autenticadas do Vet Tech, com controles acessíveis e apresentação adequada a telas largas e estreitas. Mantém opções de áreas futuras visíveis sem encaminhar o tutor a páginas inexistentes.

## ADDED Requirements

### Requirement: Navegação lateral reutilizável e com área ativa identificável
O sistema SHALL apresentar nas áreas autenticadas uma navegação lateral compartilhada com a marca Vet Tech e as opções Dashboard, Prontuário, Vacinas, Consultas, Exames, Meus Pets e Configurações. A opção correspondente à área atual SHALL ser identificada visualmente como ativa e a patinha da marca SHALL usar a mesma cor do texto “Vet Tech”.

#### Scenario: Perfil do tutor identifica Meus Pets como área ativa
- **WHEN** o tutor autenticado visualiza o perfil atual
- **THEN** a opção “Meus Pets” aparece ativa e as demais opções permanecem visíveis

#### Scenario: Navegação usada em outra área autenticada
- **WHEN** outra tela autenticada integra a navegação compartilhada e informa sua área atual
- **THEN** a mesma navegação é apresentada com essa área ativa, sem duplicar sua composição visual

### Requirement: Áreas sem tela implementada não causam navegação inválida
O sistema SHALL manter visíveis as opções de navegação de áreas ainda não implementadas sem encaminhar o tutor a uma rota inexistente. Essas opções SHALL indicar discretamente que a área estará disponível em breve ou não iniciar navegação.

#### Scenario: Tutor seleciona área ainda não implementada
- **WHEN** o tutor aciona uma opção sem tela disponível
- **THEN** o sistema não navega para uma rota inexistente nem apresenta erro 404

### Requirement: Navegação lateral adapta-se a desktop e dispositivos móveis
O sistema SHALL manter sempre visível um controle acessível para alternar a navegação. Em desktop, SHALL permitir alternar entre modo expandido e rail, usando transição suave e redimensionando a área de conteúdo sem sobreposição ou rolagem horizontal. Em viewports abaixo de 768 px, SHALL apresentar a navegação como drawer sobreposto, fechado por padrão, com backdrop que fecha o drawer quando acionado.

#### Scenario: Alternância da navegação em desktop
- **WHEN** o tutor alterna o controle de navegação em viewport desktop
- **THEN** o menu muda suavemente entre largura expandida de aproximadamente 260 px e rail de aproximadamente 72–80 px
- **AND** o conteúdo ocupa o espaço restante sem sobreposição ou rolagem horizontal

#### Scenario: Abertura e fechamento do drawer móvel
- **WHEN** o tutor abre o controle de navegação em viewport abaixo de 768 px
- **THEN** o drawer é exibido sobre o conteúdo com backdrop e o conteúdo continua ocupando a largura disponível
- **AND** acionar o backdrop ou pressionar Esc fecha o drawer

### Requirement: Estado da navegação é compartilhado e acessível
O sistema SHALL manter o estado de navegação em um estado compartilhado entre as telas autenticadas, para que a preferência de expansão seja consistente durante a navegação. O controle SHALL ser operável por teclado e expor rótulo acessível, estado expandido e indicador de foco visível.

#### Scenario: Navegação entre telas preserva a preferência
- **WHEN** o tutor alterna a navegação e segue para outra tela autenticada
- **THEN** a preferência compartilhada de navegação permanece consistente entre as telas

#### Scenario: Controle de navegação operado por teclado
- **WHEN** o tutor alcança o controle usando teclado
- **THEN** consegue alterná-lo, identifica seu propósito e estado expandido por tecnologia assistiva e visualiza o foco
