## ADDED Requirements

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
