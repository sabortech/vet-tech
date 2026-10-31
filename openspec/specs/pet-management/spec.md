# pet-management Specification

## Purpose

Permite que tutores autenticados cadastrem pets e consultem a própria lista de animais, preservando o vínculo obrigatório entre cada pet e seu tutor e sem expor dados de outros tutores.

## Requirements

### Requirement: A identidade autenticada corresponde a um tutor
O sistema SHALL autenticar o tutor usando a entidade `tutor` do modelo de domínio e SHALL disponibilizar o identificador desse tutor às operações protegidas. O fluxo SHALL funcionar sem depender da entidade `user` ou de tabelas externas ao modelo de domínio.

#### Scenario: Tutor autenticado acessa o perfil
- **WHEN** um tutor fornece credenciais válidas
- **THEN** o sistema estabelece uma sessão autenticada vinculada ao registro correspondente em `tutor`

#### Scenario: Credenciais inválidas
- **WHEN** uma pessoa tenta autenticar com credenciais inválidas
- **THEN** o sistema nega a autenticação e não concede acesso às operações do perfil

### Requirement: Tutor cadastra um pet próprio
O sistema SHALL permitir que um tutor autenticado cadastre um pet com nome e espécie. O pet SHALL ser associado exatamente a esse tutor, sem aceitar do cliente um identificador de tutor que permita associar o registro a outra pessoa. O cadastro SHALL aceitar raça opcional para representar animais sem raça definida e os demais dados do pet definidos no modelo de domínio.

#### Scenario: Cadastro válido
- **WHEN** o tutor autenticado envia nome e espécie válidos, com ou sem os demais dados opcionais
- **THEN** o sistema cria o pet associado ao tutor autenticado e confirma o cadastro

#### Scenario: Tentativa de informar outro tutor
- **WHEN** o cliente inclui no pedido um identificador de tutor diferente ou tenta definir manualmente o proprietário
- **THEN** o sistema ignora ou rejeita esse valor e associa o pet exclusivamente ao tutor autenticado

#### Scenario: Dados obrigatórios ausentes ou espécie inexistente
- **WHEN** o pedido não contém nome ou espécie válida
- **THEN** o sistema rejeita o cadastro, informa os campos que precisam de correção e não cria o pet

### Requirement: Raça pertence à espécie selecionada
Quando uma raça for informada, o sistema SHALL confirmar que ela pertence à espécie selecionada. O sistema SHALL permitir raça não informada para representar um pet SRD.

#### Scenario: Raça compatível com espécie
- **WHEN** o tutor cadastra um pet com uma raça pertencente à espécie selecionada
- **THEN** o sistema aceita o vínculo entre pet, raça e espécie

#### Scenario: Raça incompatível com espécie
- **WHEN** o tutor seleciona uma raça pertencente a uma espécie diferente da selecionada
- **THEN** o sistema rejeita o cadastro e não cria um vínculo inconsistente

#### Scenario: Pet sem raça definida
- **WHEN** o tutor cadastra um pet sem informar raça
- **THEN** o sistema aceita o cadastro com raça vazia e mantém a espécie informada

### Requirement: Tutor consulta opções de espécie e raça
O sistema SHALL disponibilizar ao tutor autenticado as espécies existentes e SHALL permitir consultar as raças associadas a uma espécie específica, usando os cadastros de domínio como fonte de verdade. Requisições sem autenticação SHALL ser negadas.

#### Scenario: Carregar espécies
- **WHEN** um tutor autenticado solicita as opções de espécie
- **THEN** o sistema retorna as espécies cadastradas com identificadores utilizáveis no cadastro do pet

#### Scenario: Carregar raças da espécie selecionada
- **WHEN** um tutor autenticado solicita raças para uma espécie existente
- **THEN** o sistema retorna somente raças associadas à espécie informada

#### Scenario: Espécie sem raças cadastradas
- **WHEN** um tutor autenticado solicita raças para uma espécie válida sem raças associadas
- **THEN** o sistema retorna uma lista vazia e o cadastro continua permitindo raça não informada

#### Scenario: Consulta de catálogo sem autenticação
- **WHEN** uma pessoa não autenticada solicita espécies ou raças
- **THEN** o sistema nega a consulta

### Requirement: Tutor lista somente os próprios pets
O sistema SHALL retornar ao tutor autenticado somente pets cujo vínculo de propriedade aponta para seu próprio registro em `tutor`. O filtro de proprietário SHALL ser derivado da sessão autenticada e não de um identificador fornecido pelo cliente. Para cada pet, a resposta SHALL incluir a foto já associada em formato consumível para exibição quando houver imagem, sem alterar os demais nomes de campos existentes.

#### Scenario: Tutor possui pets cadastrados
- **WHEN** o tutor autenticado solicita sua lista de pets
- **THEN** o sistema retorna todos e somente os pets vinculados a esse tutor
- **AND** inclui a foto de cada pet quando houver imagem associada, sem alterar os demais campos da resposta

#### Scenario: Tutor ainda não possui pets
- **WHEN** o tutor autenticado solicita sua lista e não há pets vinculados a ele
- **THEN** o sistema retorna uma lista vazia

#### Scenario: Tentativa de consultar pets de outro tutor
- **WHEN** o cliente tenta alterar ou fornecer o identificador usado para filtrar a lista
- **THEN** o sistema continua retornando somente os pets do tutor autenticado
- **AND** não expõe imagens associadas a pets de outros tutores

#### Scenario: Pet não possui foto
- **WHEN** o tutor autenticado solicita a lista e um pet não possui imagem associada
- **THEN** o sistema mantém o pet na lista sem fabricar uma imagem

### Requirement: Operações de pets exigem autenticação e não permitem edição nesta etapa
O sistema SHALL exigir autenticação de tutor para cadastrar, listar ou consultar individualmente pets e SHALL disponibilizar essas operações no escopo desta capacidade. Consulta individual SHALL verificar propriedade no backend. Edição e exclusão dos dados de pets não fazem parte desta etapa.

#### Scenario: Requisição sem autenticação
- **GIVEN** uma pessoa não possui autenticação válida de tutor
- **WHEN** tenta cadastrar, listar ou consultar individualmente pets
- **THEN** o sistema nega a operação sem criar nem revelar registros

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

### Requirement: Foto do pet é armazenada como texto base64
O sistema SHALL aceitar no cadastro de pet uma foto opcional enviada como texto no formato data URI (`data:<content-type>;base64,<conteúdo>`) e SHALL persisti-la sem transformação na coluna de texto `foto` do pet. As leituras de pet que retornam a foto SHALL devolver esse mesmo texto, aplicando os mesmos filtros de propriedade já exigidos para o pet.

#### Scenario: Cadastro com foto em base64
- **GIVEN** um tutor autenticado
- **WHEN** envia o cadastro de um pet válido com `foto` em data URI base64
- **THEN** o sistema cria o pet associado ao tutor autenticado com o texto recebido na coluna `foto`

#### Scenario: Cadastro sem foto
- **GIVEN** um tutor autenticado
- **WHEN** envia o cadastro de um pet válido sem o campo `foto`
- **THEN** o sistema cria o pet com `foto` vazia e sem fabricar uma imagem

#### Scenario: Leitura da foto de pet de outro tutor
- **GIVEN** um tutor autenticado que não é proprietário de um pet com foto
- **WHEN** solicita a lista ou o detalhe de pets
- **THEN** o sistema não retorna o texto da foto desse pet
