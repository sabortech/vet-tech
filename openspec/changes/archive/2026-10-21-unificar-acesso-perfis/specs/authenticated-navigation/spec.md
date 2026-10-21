## Purpose

Organizar a área autenticada do tutor com navegação consistente por pet e acesso ao cadastro e alternância existentes, preparando os próximos módulos clínicos.

## ADDED Requirements

### Requirement: Menu retrátil preserva o contexto
O sistema SHALL exibir Início, Vacinas, Medicamentos, Doenças e Consultas nessa ordem, com Novo pet e Mudar pet na parte inferior. O menu SHALL recolher e expandir sem alterar o pet ativo; a seção ativa e o pet atual SHALL ser identificáveis, com nomes acessíveis e operação por teclado em desktop e celular.

#### Scenario: Recolher menu
- **WHEN** o tutor recolhe e expande o menu com um pet aberto
- **THEN** o pet continua selecionado e os controles permanecem identificáveis e utilizáveis

#### Scenario: Celular
- **WHEN** o tutor navega em uma tela estreita
- **THEN** consegue alcançar menu, conteúdo e ações inferiores sem corte ou rolagem horizontal

### Requirement: Início e seções seguem o pet autorizado
O sistema SHALL apresentar em Início os dados básicos disponíveis do pet validado e usar a mesma seleção nas demais seções. Sem pet selecionado SHALL orientar escolha/cadastro. As seções clínicas ainda não implementadas SHALL indicar indisponibilidade, sem dados fictícios ou ações que simulem atendimento.

#### Scenario: Nova sessão sem seleção
- **WHEN** o tutor entra mesmo possuindo um único pet
- **THEN** recebe orientação de escolha explícita sem seleção automática

#### Scenario: Troca de animal
- **WHEN** o tutor muda de pet
- **THEN** os dados anteriores deixam de aparecer e somente a resposta da seleção atual pode preencher Início ou outra seção

### Requirement: Novo pet abre cadastro em modal
O sistema SHALL abrir o cadastro existente em modal por Novo pet, removendo-o da apresentação permanente de Início. O modal SHALL permitir teclado, foco inicial, fechamento e retorno de foco; cancelar SHALL NOT criar pet. Sucesso SHALL atualizar a lista sem trocar silenciosamente o pet ativo; falhas SHALL manter correção e nova tentativa disponíveis.

#### Scenario: Cancelar cadastro
- **WHEN** o tutor fecha o modal sem submeter
- **THEN** nenhum registro é criado e o foco volta ao controle de abertura

#### Scenario: Cadastro válido
- **WHEN** a API confirma o novo pet
- **THEN** a lista é atualizada e o pet previamente selecionado permanece o mesmo, sujeito à revalidação existente

### Requirement: Mudar pet reutiliza seleção segura
O sistema SHALL oferecer a lista dos pets próprios por Mudar pet e permitir nova escolha, mantendo as validações de propriedade, limpeza de contexto e descarte de respostas atrasadas existentes. Logout SHALL permanecer acessível.

#### Scenario: Escolher outro pet
- **GIVEN** o tutor possui A aberto e também é dono de B
- **WHEN** aciona Mudar pet e escolhe B
- **THEN** os dados de A são limpos e B só é exibido após autorização do backend
