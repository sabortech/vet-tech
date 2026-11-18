# Spec Delta

## MODIFIED Requirements

### Requirement: Navegação lateral reutilizável e com área ativa identificável
O sistema SHALL apresentar nas áreas autenticadas uma navegação lateral compartilhada com a marca Vet Tech e as opções Dashboard, Prontuário, Vacinas, Medicamentos, Doenças, Consultas, Exames, Meus Pets, Adoção e Configurações. A opção correspondente à área atual SHALL ser identificada visualmente como ativa e a patinha da marca SHALL usar a mesma cor do texto “Vet Tech”. No modo expandido, os itens SHALL ter área de interação de aproximadamente 48 px de altura e o item ativo SHALL manter o destaque branco com cantos arredondados.

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
- **WHEN** o tutor navega entre Meus Pets, Adoção, Configurações e Prontuário
- **THEN** encontra a mesma sidebar verde personalizada, marca, ordem de itens, ícones, dimensões, foco e destaque ativo
- **AND** o tema escuro usa os tokens da mesma identidade visual, sem trocar para um menu de aparência padrão

#### Scenario: Seção clínica ativa
- **WHEN** o tutor abre Vacinas, Medicamentos, Doenças ou Consultas
- **THEN** somente a seção clínica correspondente é marcada como atual, sem manter outro item ativo simultaneamente
