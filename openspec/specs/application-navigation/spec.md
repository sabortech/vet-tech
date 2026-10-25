# application-navigation Specification

## Purpose

Oferece navegação consistente entre as áreas autenticadas do Vet Tech, com controles acessíveis e apresentação adequada a telas largas e estreitas. Mantém opções de áreas futuras visíveis sem encaminhar o tutor a páginas inexistentes.

## Requirements

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

### Requirement: Áreas sem tela implementada não causam navegação inválida
O sistema SHALL manter visíveis as opções de navegação de áreas ainda não implementadas sem encaminhar o tutor a uma rota inexistente. Essas opções SHALL indicar discretamente que a área estará disponível em breve ou não iniciar navegação.

#### Scenario: Tutor seleciona área ainda não implementada
- **WHEN** o tutor aciona uma opção sem tela disponível
- **THEN** o sistema não navega para uma rota inexistente nem apresenta erro 404

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

### Requirement: Estado da navegação é compartilhado e acessível
O sistema SHALL manter o estado de navegação em um estado compartilhado entre as telas autenticadas, para que a preferência de expansão seja consistente durante a navegação. O controle SHALL ser operável por teclado e expor rótulo acessível, estado expandido e indicador de foco visível.

#### Scenario: Navegação entre telas preserva a preferência
- **WHEN** o tutor alterna a navegação e segue para outra tela autenticada
- **THEN** a preferência compartilhada de navegação permanece consistente entre as telas

#### Scenario: Controle de navegação operado por teclado
- **WHEN** o tutor alcança o controle usando teclado
- **THEN** consegue alterná-lo, identifica seu propósito e estado expandido por tecnologia assistiva e visualiza o foco

### Requirement: Configurações possui rota autenticada e acesso pela sidebar
O sistema SHALL disponibilizar `/configuracoes` para o tutor autenticado, tornar Configurações navegável na sidebar compartilhada e preservar o acesso a Meus Pets na rota atual. Acesso sem sessão válida SHALL conduzir ao login sem exibir dados pessoais ou iniciar consultas autenticadas de conta. As áreas futuras SHALL continuar sem navegação inválida.

#### Scenario: Tutor abre Configurações pelo menu
- **WHEN** o tutor seleciona Configurações
- **THEN** acessa `/configuracoes` com o item ativo e pode retornar a Meus Pets usando o mesmo menu

#### Scenario: Acesso direto sem sessão
- **WHEN** uma pessoa não autenticada abre `/configuracoes`, inclusive após recarregar sem sessão restaurada
- **THEN** é conduzida ao login sem visualizar dados de conta

### Requirement: Saída de formulário alterado exige decisão de descarte
O sistema SHALL solicitar confirmação antes de abandonar dados pessoais alterados ao trocar de aba, navegar pelo menu ou acionar Sair. SHALL oferecer Continuar editando e Descartar alterações; somente o descarte confirmado executa a intenção original. Para fechamento ou recarga da página SHALL usar a confirmação nativa quando suportada pelo navegador, sem prometer interceptação universal.

#### Scenario: Tutor decide continuar editando
- **GIVEN** há dados pessoais alterados e não salvos
- **WHEN** o tutor tenta sair e escolhe Continuar editando
- **THEN** permanece na seção com os campos preservados e o foco retorna ao controle apropriado

#### Scenario: Tutor confirma descarte
- **GIVEN** há dados pessoais alterados e não salvos
- **WHEN** confirma Descartar alterações
- **THEN** descarta somente as edições e executa a troca de aba, navegação ou saída solicitada

#### Scenario: Formulário sem alterações
- **WHEN** o tutor navega sem alterações pendentes
- **THEN** a navegação ocorre sem confirmação desnecessária

### Requirement: Navegação limpa não espera leitura remota de conta
O sistema SHALL permitir trocar entre Meus Pets e Configurações sem aguardar
consulta remota de conta nem confirmação do servidor quando não houver edição
pendente. Uma consulta em andamento SHALL manter navegação e abas responsivas.

#### Scenario: Consulta de conta em andamento
- **WHEN** o tutor navega enquanto a leitura de dados da conta está pendente
- **THEN** a navegação ocorre e a leitura não bloqueia a fila de eventos da interface

#### Scenario: Reentrada recente na mesma sessão
- **WHEN** o tutor volta às configurações em até 60 segundos após carregar os dados
- **THEN** os dados confirmados da mesma sessão podem ser reutilizados sem nova leitura, preservando isolamento entre contas
