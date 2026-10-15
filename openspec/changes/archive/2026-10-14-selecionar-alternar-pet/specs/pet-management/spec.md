# Delta de seleção e alternância de pet

## ADDED Requirements

### Requirement: Tutor abre somente um pet próprio
O sistema SHALL permitir consultar individualmente os dados básicos de um pet, exigindo autenticação e verificando no backend que o pet pertence ao tutor da sessão. Um identificador fornecido pelo cliente SHALL ser tratado somente como alvo da consulta, nunca como comprovação de propriedade (RN05).

#### Scenario: Abrir pet do próprio tutor
- **GIVEN** um tutor autenticado possui um pet
- **WHEN** solicita a abertura desse pet
- **THEN** o sistema verifica a propriedade no backend e retorna somente os dados básicos desse animal

#### Scenario: Tentar abrir pet de outro tutor
- **GIVEN** um tutor autenticado conhece o identificador de um pet alheio
- **WHEN** envia esse identificador diretamente à operação de consulta individual, mesmo sem usar a lista da interface
- **THEN** o sistema nega a leitura sem revelar dados nem confirmar se o identificador pertence a outro tutor

#### Scenario: Identificador inválido ou inexistente
- **WHEN** o tutor solicita um identificador malformado ou inexistente
- **THEN** o sistema não abre um animal e informa que a solicitação é inválida ou o pet não está disponível, sem revelar dados de terceiros

### Requirement: Área do pet identifica a seleção atual
O sistema SHALL permitir abrir um pet a partir da lista e apresentar seu nome, espécie, raça, sexo, nascimento, peso, pelagem e microchip quando disponíveis. A seleção SHALL ser explícita, inclusive quando houver um único pet. Campos opcionais ausentes ou falhas nos nomes de catálogo SHALL NOT impedir a exibição dos dados autorizados.

#### Scenario: Entrar com pets cadastrados
- **WHEN** o tutor entra e sua lista contém um ou mais pets
- **THEN** pode escolher qual abrir e nenhum pet é selecionado automaticamente

#### Scenario: Pet aberto com dados opcionais ausentes
- **WHEN** o tutor abre um pet próprio sem raça e sem outros dados opcionais
- **THEN** vê o pet identificado, a raça como SRD e os demais dados ausentes sem valores inventados

#### Scenario: Catálogo indisponível
- **WHEN** os dados básicos do pet são autorizados mas não é possível resolver o nome de espécie ou raça
- **THEN** o sistema mantém os dados do pet acessíveis, usa identificação genérica para o vínculo não resolvido e informa a falha

#### Scenario: Tutor sem pets
- **WHEN** a lista autorizada está vazia
- **THEN** nenhuma seleção é mantida e o cadastro de pet permanece acessível

### Requirement: Alternância não mistura contextos de pets
O sistema SHALL permitir alternar entre os pets do tutor e voltar à lista. Ao iniciar outra seleção, SHALL deixar de apresentar os detalhes anteriores. Somente a resposta correspondente à última seleção e à sessão atual SHALL preencher a área do pet; respostas anteriores, inclusive erros, SHALL NOT substituir o contexto atual.

#### Scenario: Trocar de um pet para outro
- **GIVEN** o tutor abriu seu pet A e também possui B
- **WHEN** escolhe B
- **THEN** os detalhes de A deixam de aparecer e somente os dados autorizados de B são exibidos ao concluir o carregamento

#### Scenario: Resposta antiga chega depois da seleção atual
- **WHEN** o tutor escolhe A e depois B, e a resposta de A chega por último
- **THEN** a resposta de A é descartada e não altera dados, mensagem ou carregamento de B

#### Scenario: Voltar à lista durante carregamento
- **WHEN** o tutor volta à lista antes de concluir a abertura de um pet
- **THEN** a seleção é limpa e a resposta pendente não reabre o animal

### Requirement: Falhas de abertura permitem recuperação sem exibir outro pet
O sistema SHALL apresentar estado de carregamento, falha e nova tentativa na abertura do pet. Se a seleção falhar, SHALL manter acessível a lista para escolher outro animal e não exibir os detalhes de uma seleção anterior como se fossem os do pet solicitado.

#### Scenario: Falha ao abrir outro pet
- **WHEN** o tutor troca de A para B e a consulta de B falha
- **THEN** vê a falha, não vê os detalhes de A como se fossem B e pode tentar novamente ou escolher outro pet

#### Scenario: Seleção deixa de estar disponível após atualização
- **WHEN** uma atualização bem-sucedida da lista não contém mais o pet selecionado
- **THEN** a seleção e seus detalhes são limpos, sem escolher outro pet automaticamente

#### Scenario: Atualizar a lista mantendo o pet
- **WHEN** uma atualização bem-sucedida da lista ainda contém o pet selecionado
- **THEN** o sistema revalida seus detalhes no backend antes de reapresentá-los como atuais

### Requirement: Seleção pertence somente à sessão atual
O sistema SHALL limpar seleção, detalhes e operações pendentes ao encerrar a sessão, reconhecer autenticação inválida ou estabelecer outra identidade. A seleção SHALL permanecer somente no contexto da sessão ativa e SHALL NOT ser restaurada de armazenamento persistente. Respostas de uma sessão encerrada SHALL NOT preencher a seguinte.

#### Scenario: Logout durante abertura
- **WHEN** o tutor sai enquanto o carregamento de um pet está em andamento
- **THEN** nenhum dado da seleção permanece visível nem é restaurado pela resposta atrasada

#### Scenario: Outra conta entra
- **GIVEN** uma conta possuía pet selecionado
- **WHEN** outra conta estabelece uma sessão
- **THEN** a nova sessão inicia sem seleção anterior, mesmo se a nova listagem falhar

#### Scenario: Token inválido na abertura
- **WHEN** o backend rejeita a autenticação da consulta individual
- **THEN** o sistema limpa a seleção e exige nova autenticação antes de permitir outra abertura

## MODIFIED Requirements

### Requirement: Operações de pets exigem autenticação e não permitem edição nesta etapa
O sistema SHALL exigir autenticação de tutor para cadastrar, listar ou consultar individualmente pets e SHALL disponibilizar essas operações no escopo desta capacidade. Consulta individual SHALL verificar propriedade no backend. Edição e exclusão dos dados de pets não fazem parte desta etapa.

#### Scenario: Requisição sem autenticação
- **GIVEN** uma pessoa não possui autenticação válida de tutor
- **WHEN** tenta cadastrar, listar ou consultar individualmente pets
- **THEN** o sistema nega a operação sem criar nem revelar registros
