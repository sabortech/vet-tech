# pet-clinical-loading Specification

## Purpose

Permitir ao tutor navegar pelas seções clínicas do pet sem consultas repetidas, com carregamento identificável, dados temporários isolados por sessão e recuperação segura de falhas.

## Requirements

### Requirement: Seleção prepara os dados clínicos do pet
O sistema SHALL iniciar o carregamento dos dados básicos, histórico publicado e consultas ao selecionar explicitamente um pet próprio. O conjunto clínico SHALL atender Vacinas, Medicamentos, Doenças e Consultas sem exigir nova leitura por seção enquanto válido.

#### Scenario: Primeira seleção
- **GIVEN** o tutor autenticado possui um pet disponível
- **WHEN** seleciona esse pet
- **THEN** o sistema consulta seus dados básicos, histórico e consultas sem aguardar a abertura de uma seção clínica
- **AND** somente dados autorizados pelo backend preenchem a área

#### Scenario: Navegar entre seções carregadas
- **WHEN** o tutor alterna entre as seções com dados válidos do mesmo pet
- **THEN** o conteúdo usa o conjunto já carregado e nenhuma nova consulta clínica é disparada apenas pela mudança de seção

### Requirement: Loading mantém a navegação disponível
O sistema SHALL mostrar indicador visual de carregamento com texto acessível e região ocupada identificável enquanto aguarda os dados do pet. A navegação, a escolha de outro pet e a saída SHALL permanecer disponíveis. Dados de outro pet e mensagens de lista vazia SHALL NOT substituir o loading.

#### Scenario: Rede lenta
- **WHEN** uma leitura clínica permanece pendente
- **THEN** o tutor vê spinner ou skeleton acompanhado de “Carregando dados do pet…”
- **AND** consegue trocar de seção ou pet antes de a leitura terminar
- **AND** o sistema não duplica a leitura em andamento ao trocar de seção

#### Scenario: Resposta vazia válida
- **WHEN** a consulta termina com sucesso sem registros
- **THEN** o loading termina e a seção mostra seu estado vazio

### Requirement: Reutilização temporária tem atualização explícita
O sistema SHALL reutilizar o conjunto carregado com sucesso por até 60 segundos na seleção atual. Após esse prazo, o próximo acesso clínico SHALL revalidá-lo com loading. Uma ação Atualizar SHALL forçar revalidação. Falhas SHALL NOT renovar a validade, e o sistema SHALL NOT realizar polling contínuo.

#### Scenario: Dados expirados
- **WHEN** o tutor abre uma seção após 60 segundos do carregamento confirmado
- **THEN** o sistema inicia uma única revalidação e identifica a espera antes de apresentar os dados como atuais

#### Scenario: Atualização manual
- **WHEN** o tutor aciona Atualizar antes de expirar o conjunto
- **THEN** o sistema consulta novamente os dados e impede carregamentos duplicados para a mesma seleção

### Requirement: Respostas pertencem à seleção e sessão atuais
O sistema SHALL invalidar o conjunto ao trocar ou remover a seleção, sair, expirar a sessão ou receber negação de acesso. Uma resposta antiga SHALL NOT alterar dados, erros ou loading da seleção atual. Dados clínicos SHALL permanecer isolados na sessão do servidor e SHALL NOT ser persistidos no navegador ou compartilhados entre usuários.

#### Scenario: Troca rápida de pets
- **GIVEN** a leitura de A está pendente
- **WHEN** o tutor seleciona B e a resposta de A chega depois
- **THEN** a resposta de A é descartada e somente a leitura de B pode concluir seu loading

#### Scenario: Saída durante consulta
- **WHEN** o tutor sai ou volta à lista durante uma leitura
- **THEN** o contexto é limpo e a resposta pendente não reabre nem preenche o pet

#### Scenario: Propriedade negada
- **GIVEN** o cliente solicita um pet sem propriedade autorizada
- **WHEN** o backend nega a consulta
- **THEN** nenhum dado desse pet nem cópia anterior é apresentado como disponível

### Requirement: Falhas permitem recuperação sem mascarar os dados
O sistema SHALL terminar o loading ao falhar uma leitura atual, apresentar mensagem segura e permitir Tentar novamente ou escolher outro pet. Falha de rede ou serviço SHALL NOT apagar dados básicos já autorizados; negação de acesso SHALL limpar o contexto protegido. Um conjunto clínico incompleto SHALL NOT ser apresentado como carregado com sucesso.

#### Scenario: Falha em uma das leituras clínicas
- **WHEN** o histórico responde mas a consulta das reservas falha
- **THEN** o sistema não marca o conjunto clínico como completo nem exibe ausência de reservas como resultado confirmado
- **AND** preserva os dados básicos autorizados e oferece nova tentativa

#### Scenario: Serviço limita solicitações
- **WHEN** o Xano responde 429 e o cliente aguarda a tentativa permitida
- **THEN** o loading permanece visível, a navegação continua disponível e o encerramento das tentativas oferece recuperação

### Requirement: Operações atualizam os dados relacionados
O sistema SHALL invalidar e revalidar dados relacionados após uma operação confirmada de agendamento ou alteração de consentimento. Um resultado de leitura iniciado antes da operação SHALL NOT substituir a atualização posterior. Falhas de escrita SHALL NOT mostrar sucesso nem disparar repetição automática da escrita por causa do carregamento.

#### Scenario: Agendamento confirmado
- **WHEN** o tutor confirma um agendamento para o pet selecionado
- **THEN** a próxima apresentação das consultas reflete uma leitura posterior à confirmação

#### Scenario: Alterar consentimento
- **WHEN** o backend confirma uma mudança de consentimento
- **THEN** a lista de autorizações é revalidada sem reconsultar seções não afetadas apenas por navegação

### Requirement: Consultas auxiliares preservam autorização e auditoria
O sistema SHALL consultar autorizações e auditoria somente quando a área correspondente for solicitada e validar seu acesso no backend. SHALL preservar a auditoria exigida das leituras remotas. O reaproveitamento descrito nesta capacidade SHALL restringir-se ao tutor; leituras veterinárias SHALL manter suas verificações de consentimento e auditoria existentes.

#### Scenario: Abrir somente Vacinas
- **WHEN** o tutor seleciona o pet e consulta Vacinas
- **THEN** o carregamento inicial não consulta autorizações nem auditoria

#### Scenario: Consultar informações auxiliares
- **GIVEN** o tutor está autenticado
- **WHEN** solicita autorizações ou auditoria do pet
- **THEN** o backend verifica propriedade e retorna apenas os dados autorizados
- **AND** os registros de auditoria existentes não são removidos ou alterados pela otimização
