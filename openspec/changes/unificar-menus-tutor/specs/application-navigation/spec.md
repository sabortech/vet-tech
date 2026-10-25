# Spec Delta

## MODIFIED Requirements

### Requirement: Navegação lateral reutilizável e com área ativa identificável
O sistema SHALL apresentar nas áreas autenticadas uma navegação lateral compartilhada com a marca Vet Tech e as opções Dashboard, Prontuário, Vacinas, Medicamentos, Doenças, Consultas, Exames, Meus Pets e Configurações. A opção correspondente à área atual SHALL ser identificada visualmente como ativa e a patinha da marca SHALL usar a mesma cor do texto “Vet Tech”. No modo expandido, os itens SHALL ter área de interação de aproximadamente 48 px de altura e o item ativo SHALL manter o destaque branco com cantos arredondados.

#### Scenario: Perfil do tutor identifica Meus Pets como área ativa
- **WHEN** o tutor autenticado visualiza o perfil atual
- **THEN** a opção “Meus Pets” aparece ativa e as demais opções permanecem visíveis

#### Scenario: Navegação usada em outra área autenticada
- **WHEN** outra tela autenticada integra a navegação compartilhada e informa sua área atual
- **THEN** a mesma navegação é apresentada com essa área ativa, sem duplicar sua composição visual

#### Scenario: Marca mantém proporção e cor consistentes
- **WHEN** a sidebar aparece em modo expandido ou recolhido
- **THEN** a patinha e o texto “Vet Tech” usam o mesmo token de cor e a marca e os itens permanecem alinhados sem cortes

#### Scenario: Tutor alterna entre áreas com o mesmo design
- **WHEN** o tutor navega entre Meus Pets, Configurações e Prontuário
- **THEN** encontra a mesma sidebar verde personalizada, marca, ordem de itens, ícones, dimensões, foco e destaque ativo
- **AND** o tema escuro usa os tokens da mesma identidade visual, sem trocar para um menu de aparência padrão

#### Scenario: Seção clínica ativa
- **WHEN** o tutor abre Vacinas, Medicamentos, Doenças ou Consultas
- **THEN** somente a seção clínica correspondente é marcada como atual, sem manter outro item ativo simultaneamente

### Requirement: Navegação lateral adapta-se a desktop e dispositivos móveis
O sistema SHALL manter sempre visível um controle acessível para alternar a navegação. Em desktop, SHALL permitir alternar entre modo expandido de aproximadamente 260 px e rail de aproximadamente 72–80 px, usando transição suave e redimensionando a área de conteúdo restante sem sobreposição ou rolagem horizontal. A adaptação do conteúdo SHALL considerar o espaço disponível após a sidebar, e não somente a largura total da viewport. Em viewports abaixo de 768 px, SHALL apresentar a navegação como drawer sobreposto, fechado por padrão, com backdrop que fecha o drawer quando acionado.

#### Scenario: Alternância da navegação em desktop
- **WHEN** o tutor alterna o controle de navegação em viewport desktop
- **THEN** o menu muda suavemente entre largura expandida e rail, e o conteúdo usa o espaço restante sem sobreposição ou rolagem horizontal

#### Scenario: Itens do rail recolhido ficam centralizados
- **WHEN** a sidebar está recolhida em desktop
- **THEN** os ícones dos itens de navegação ficam centralizados no eixo vertical da sidebar, alinhados com a patinha da marca e o botão de alternar
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

#### Scenario: Navegação fecha o drawer
- **WHEN** o tutor conclui uma navegação pelo drawer móvel
- **THEN** o drawer fecha e o conteúdo de destino fica acessível sem backdrop residual
- **AND** cancelar uma confirmação de descarte mantém a tela atual e devolve foco ao controle apropriado

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

#### Scenario: Descarte preserva o destino clínico
- **GIVEN** existem dados pessoais alterados em Configurações
- **WHEN** o tutor escolhe Vacinas no menu e confirma Descartar alterações
- **THEN** segue para Vacinas no Prontuário, preservando a seleção autorizada do pet
- **AND** não é encaminhado a Meus Pets por um destino fixo do guard

## ADDED Requirements

### Requirement: Entradas clínicas do menu conduzem à seção existente
O sistema SHALL disponibilizar Prontuário, Vacinas, Medicamentos, Doenças e Consultas no menu compartilhado do tutor. Prontuário SHALL abrir o resumo Início. A navegação SHALL preservar a seleção autorizada e, sem pet selecionado, solicitar escolha explícita sem inventar dados ou selecionar um animal automaticamente.

#### Scenario: Abrir seção a partir de Meus Pets
- **GIVEN** o tutor tem um pet selecionado e autorizado
- **WHEN** aciona Medicamentos pelo menu de Meus Pets
- **THEN** abre essa seção no Prontuário usando o mesmo pet

#### Scenario: Entrar em seção sem pet
- **WHEN** o tutor aciona uma seção clínica sem pet selecionado
- **THEN** vê a orientação e a lista para escolher um pet, mantendo a seção pretendida identificável
- **AND** o sistema não consulta dados clínicos sem uma seleção autorizada

#### Scenario: Áreas futuras continuam indisponíveis
- **WHEN** o tutor aciona Dashboard ou Exames ainda sem tela implementada
- **THEN** permanece na tela atual e não recebe erro 404
