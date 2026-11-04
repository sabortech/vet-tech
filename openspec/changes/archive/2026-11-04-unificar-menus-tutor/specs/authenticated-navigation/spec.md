# Spec Delta

## MODIFIED Requirements

### Requirement: Menu retrátil preserva o contexto
O sistema SHALL usar no Prontuário o mesmo menu personalizado das outras telas do tutor. Prontuário SHALL representar Início; Vacinas, Medicamentos, Doenças e Consultas SHALL manter essa ordem relativa. Novo pet e Mudar pet SHALL permanecer na parte inferior no contexto clínico. Recolher ou expandir SHALL preservar o pet ativo; seção e pet SHALL ser identificáveis, com controles acessíveis por teclado em desktop e celular.

#### Scenario: Recolher menu
- **WHEN** o tutor recolhe e expande o menu com um pet aberto
- **THEN** o pet continua selecionado e os controles permanecem identificáveis e utilizáveis

#### Scenario: Celular
- **WHEN** o tutor navega em uma tela estreita
- **THEN** consegue alcançar menu, conteúdo e ações inferiores sem corte ou rolagem horizontal

#### Scenario: Preservar o pet entre áreas
- **GIVEN** o tutor abriu um pet autorizado
- **WHEN** visita Configurações ou Meus Pets e retorna a uma seção clínica pelo menu
- **THEN** a seção usa a mesma seleção e a preferência de expansão permanece consistente
- **AND** a navegação não limpa o pet nem dispara atualização clínica apenas por renderizar o menu

#### Scenario: Loading não bloqueia o menu compartilhado
- **WHEN** o tutor troca de seção enquanto uma leitura clínica está pendente
- **THEN** a navegação permanece disponível, o loading continua identificável e a leitura pendente não é duplicada

### Requirement: Novo pet abre cadastro em modal
O sistema SHALL abrir o cadastro existente em modal por Novo pet, removendo-o da apresentação permanente de Início. O modal SHALL permitir teclado, foco inicial, fechamento e retorno de foco; cancelar SHALL NOT criar pet. Sucesso SHALL atualizar a lista sem trocar silenciosamente o pet ativo; falhas SHALL manter correção e nova tentativa disponíveis. Abrir ou fechar o modal SHALL preservar a rota clínica atual.

#### Scenario: Cancelar cadastro
- **WHEN** o tutor fecha o modal sem submeter
- **THEN** nenhum registro é criado e o foco volta ao controle de abertura

#### Scenario: Cadastro válido
- **WHEN** a API confirma o novo pet
- **THEN** a lista é atualizada e o pet previamente selecionado permanece o mesmo, sujeito à revalidação existente

#### Scenario: Modal não redireciona ao login
- **GIVEN** o tutor está em uma seção do Prontuário
- **WHEN** abre Novo pet e depois cancela o modal
- **THEN** continua na mesma rota e seção, sem ser redirecionado para `/login`

## ADDED Requirements

### Requirement: Ações clínicas compartilham a aparência do menu
O sistema SHALL apresentar Novo pet, Mudar pet e Sair no contexto clínico usando os mesmos padrões de ícone, espaçamento, foco, tema e identificação acessível dos demais itens. Mudar pet e Sair SHALL preservar suas regras existentes de limpeza e descarte de respostas antigas.

#### Scenario: Voltar à escolha durante carregamento
- **WHEN** o tutor aciona Mudar pet enquanto aguarda uma leitura
- **THEN** retorna à escolha e a resposta antiga não reabre nem preenche o animal anterior

#### Scenario: Sair durante carregamento
- **WHEN** o tutor encerra a sessão com uma leitura clínica pendente
- **THEN** a sessão e o contexto são limpos e a resposta pendente não repõe dados no menu ou no conteúdo
