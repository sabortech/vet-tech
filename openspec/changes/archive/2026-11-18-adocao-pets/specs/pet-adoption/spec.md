# Spec Delta

## Purpose

Permite que tutores autenticados descubram pets disponibilizados para adoção, conheçam um resumo clínico autorizado e transfiram a propriedade com confirmação explícita, preservando o histórico e a privacidade do tutor anterior.

## ADDED Requirements

### Requirement: Disponibilidade para adoção depende de autorização registrada
Somente pets marcados como disponíveis por operação administrativa confiável no backend SHALL aparecer na adoção. A equipe SHALL confirmar autorização expressa do tutor atual para publicar os dados permitidos antes de marcar o pet. A disponibilidade SHALL iniciar desativada e SHALL NOT ser alterável por endpoints comuns de tutor.

#### Scenario: Pet autorizado é disponibilizado
- **GIVEN** a equipe confirmou a autorização do tutor responsável
- **WHEN** marca o pet como disponível no backend
- **THEN** o pet pode aparecer na lista de adoção para tutores autenticados

#### Scenario: Pet não disponibilizado ou sem autorização
- **GIVEN** o pet não está marcado como disponível ou a autorização de divulgação não foi confirmada
- **WHEN** um tutor solicita a lista de adoção
- **THEN** o pet e seus dados clínicos não são retornados

### Requirement: Lista agregada contém somente os dados necessários
Uma solicitação autenticada de listagem SHALL retornar os pets disponíveis em uma resposta agregada com foto, nome, espécie, raça ou SRD, sexo, idade quando calculável e peso quando cadastrado. Para cada pet, SHALL incluir somente resumo clínico autorizado: nome e data de aplicação/próxima dose da vacina mais recente; medicamentos atualmente prescritos com nome, dose, frequência, tipo e período; condições consolidadas não curadas com nome e estado; e tipo, data e estado do exame recente. O resumo SHALL NOT incluir microchip, tutor ou veterinário identificável, motivo, diagnóstico textual, observações, evolução livre, resultado textual, anexos ou rascunhos clínicos.

#### Scenario: Tutor autenticado consulta pets disponíveis
- **GIVEN** existem pets com disponibilidade e autorização válidas
- **WHEN** o tutor autenticado abre Adoção
- **THEN** recebe os dados de identificação e o resumo clínico permitido de todos os pets em uma resposta agregada

#### Scenario: Histórico clínico contém campos não autorizados para divulgação
- **GIVEN** o prontuário de um pet disponível contém notas, resultados textuais, anexos ou rascunhos
- **WHEN** o backend monta o resumo de adoção
- **THEN** esses campos não aparecem na resposta nem podem ser obtidos por essa operação

#### Scenario: Lista sem disponibilidade
- **GIVEN** nenhum pet está disponível com autorização válida
- **WHEN** o tutor autenticado solicita a lista
- **THEN** recebe uma lista vazia sem dados de pets não elegíveis

### Requirement: Pré-visualização não concede acesso ao prontuário completo
“Ver prontuário” SHALL apresentar somente o resumo já retornado para aquele pet disponível. A ação SHALL NOT solicitar seções clínicas adicionais nem contornar verificações de propriedade. O tutor adotante SHALL obter acesso ao prontuário completo somente depois da transferência confirmada, por meio das leituras autenticadas existentes para o proprietário.

#### Scenario: Consultar o resumo antes de adotar
- **GIVEN** o pet está disponível na lista carregada
- **WHEN** o tutor aciona “Ver prontuário”
- **THEN** vê somente os campos clínicos autorizados já carregados, sem nova consulta por seção ou card

#### Scenario: Prévia apresenta foto e resumo em painel dividido
- **GIVEN** o pet disponível possui foto e resumo clínico na lista já carregada
- **WHEN** o tutor aciona “Ver prontuário”
- **THEN** a prévia apresenta a foto à esquerda e as informações clínicas autorizadas à direita, separadas por um divisor visual
- **AND** não solicita novamente a foto nem os dados clínicos
- **AND** em telas estreitas empilha a foto e as informações sem perder legibilidade

#### Scenario: Tentar abrir prontuário completo antes da adoção
- **GIVEN** o tutor não é o proprietário atual do pet
- **WHEN** tenta usar uma leitura completa de prontuário com o identificador do pet
- **THEN** o backend nega a leitura e não revela conteúdo clínico completo

### Requirement: Adoção transfere propriedade usando a identidade autenticada
O backend SHALL permitir que somente um tutor autenticado adote um pet ainda disponível. O pedido SHALL identificar somente o pet-alvo; o backend SHALL obter o novo `tutor_id` exclusivamente da identidade autenticada. Em uma única operação consistente, SHALL transferir o vínculo obrigatório do pet, desativar sua disponibilidade e revogar autorizações veterinárias anteriores, preservando o histórico clínico e a auditoria existente. O sucesso SHALL retornar os dados básicos suficientes para atualizar as listas locais do tutor.

#### Scenario: Adoção confirmada
- **GIVEN** o tutor autenticado confirma a adoção de um pet disponível
- **WHEN** o backend conclui a operação
- **THEN** o pet passa a pertencer ao tutor da sessão, deixa de estar disponível, mantém seu histórico e retorna os dados básicos atualizados

#### Scenario: Cliente tenta escolher o tutor de destino
- **GIVEN** o cliente inclui um identificador de tutor no pedido de adoção
- **WHEN** a operação é processada
- **THEN** o backend ignora ou rejeita esse identificador e usa exclusivamente o tutor autenticado

#### Scenario: Dois tutores tentam adotar o mesmo pet
- **GIVEN** dois tutores autenticados confirmam a adoção do mesmo pet simultaneamente
- **WHEN** as operações concorrentes são processadas
- **THEN** no máximo uma conclui; a outra recebe uma falha explícita sem transferir o pet novamente nem alterar as listas locais

#### Scenario: Pet deixou de estar disponível
- **GIVEN** o pet foi adotado, retirado da lista ou não existe
- **WHEN** outro tutor tenta adotá-lo por identificador direto
- **THEN** o backend rejeita a operação sem revelar dados nem alterar a propriedade

#### Scenario: Requisição sem tutor autenticado
- **GIVEN** a sessão não corresponde a um tutor autenticado válido
- **WHEN** uma pessoa tenta listar ou adotar pets
- **THEN** o backend nega a operação sem retornar dados ou alterar vínculos

### Requirement: Confirmação e atualização das listas refletem somente sucesso do backend
A interface SHALL solicitar confirmação explícita antes da adoção e SHALL permitir cancelar sem enviar uma operação. Após resposta de sucesso válida, SHALL remover o pet da lista de adoção e acrescentar o pet retornado às listas locais usadas em Meus Pets e Mudar pet, sem selecionar o pet automaticamente nem fazer uma segunda consulta para refletir o sucesso. Falhas SHALL preservar o estado confirmado anterior, apresentar feedback compreensível e permitir atualização manual da lista.

#### Scenario: Tutor cancela a confirmação
- **GIVEN** o diálogo de confirmação está aberto
- **WHEN** o tutor seleciona Cancelar ou fecha o diálogo
- **THEN** nenhuma adoção é enviada e nenhuma lista é alterada

#### Scenario: Adoção bem-sucedida atualiza as listas locais
- **GIVEN** o tutor confirma uma adoção e o backend retorna o pet transferido
- **WHEN** a interface recebe uma resposta válida
- **THEN** fecha a confirmação, remove o card de adoção e inclui o pet em Meus Pets e Mudar pet sem nova leitura ao Xano

#### Scenario: Falha ou resposta incompatível
- **GIVEN** a adoção falha ou o backend retorna dados incompatíveis com o pet confirmado
- **WHEN** a interface recebe a resposta
- **THEN** não apresenta sucesso nem altera as listas, informa a falha e mantém uma recuperação explícita

#### Scenario: Sessão muda durante carregamento ou adoção
- **GIVEN** uma leitura ou adoção está pendente
- **WHEN** a sessão termina ou outra identidade é estabelecida
- **THEN** a resposta antiga não preenche a lista nem altera os pets da nova sessão

### Requirement: Demonstração local é explícita e não persiste adoções
O modo de demonstração SHALL ficar desativado por padrão e somente SHALL ser habilitado por configuração exclusiva do backend. Quando ativo, a interface SHALL identificar visualmente os perfis como fictícios, mostrar os seis perfis locais fornecidos com as fotos correspondentes e usar “Não informado” nos campos clínicos sem dados. Listagem, pré-visualização e confirmação demonstrativas SHALL NOT chamar endpoints de adoção do Xano. Confirmar SHALL remover o perfil somente do estado demonstrativo da sessão e SHALL informar que a ação não foi persistida nem atualizou os pets reais do tutor. Falhas da API real SHALL NOT ativar fixtures automaticamente.

#### Scenario: Tutor visualiza os perfis no modo demonstrativo
- **GIVEN** `VET_TECH_ADOPTION_DEMO=true` no backend e um tutor autenticado
- **WHEN** abre Adoção
- **THEN** vê Hades, Lua, Lulu, Luna, Nina e Pituco com as fotos locais, identificação fictícia e aviso persistente de demonstração, sem resumo clínico inventado ou solicitação ao endpoint de adoção

#### Scenario: Tutor confirma adoção demonstrativa
- **GIVEN** um card demonstrativo e a confirmação aberta
- **WHEN** o tutor confirma
- **THEN** o card desaparece somente do estado demonstrativo da sessão, nenhuma requisição de adoção é enviada e a mensagem esclarece que nada foi salvo no Xano ou adicionado a Meus Pets/Mudar pet

#### Scenario: Modo demonstrativo desligado ou Xano indisponível
- **GIVEN** `VET_TECH_ADOPTION_DEMO` está desligado
- **WHEN** a tela de adoção carrega ou a API Xano falha
- **THEN** o fluxo real mantém seu comportamento e exibe erro/recuperação, sem mostrar perfis de demonstração
