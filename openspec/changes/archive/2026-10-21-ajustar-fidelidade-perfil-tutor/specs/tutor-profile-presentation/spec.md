# Spec Delta

## MODIFIED Requirements

### Requirement: Perfil do tutor é remodelado na rota autenticada existente
O sistema SHALL apresentar o perfil do tutor autenticado na rota atual, sem criar outra página ou rota. A tela SHALL conter o título “Perfil do tutor”, o botão “Sair”, os cartões “Cadastrar pet” e “Meus pets” e SHALL preservar os textos, nomes de campos e ações existentes do cadastro, da atualização da lista e da saída. Em telas com espaço para duas colunas, os cartões SHALL começar alinhados no topo, compartilhar o mesmo padding interno e alinhar visualmente seus títulos.

#### Scenario: Tutor autenticado acessa o perfil
- **WHEN** um tutor autenticado acessa o perfil
- **THEN** a tela remodelada aparece na rota atual com o cadastro e a lista de pets lado a lado em desktop, cartões alinhados no topo e títulos na mesma linha visual, sem alterar os textos e ações existentes

#### Scenario: Tutor encerra a sessão pelo perfil
- **WHEN** o tutor aciona “Sair”
- **THEN** o fluxo de logout existente é executado e o acesso ao perfil continua protegido pela autenticação

### Requirement: Perfil e formulário adaptam-se à largura disponível
O sistema SHALL manter o formulário e a lista utilizáveis sem rolagem horizontal. Os cartões SHALL ficar lado a lado quando a área de conteúdo restante comportar ambos com legibilidade e SHALL empilhar quando a viewport tiver menos de aproximadamente 1100 px ou quando a sidebar reduzir a largura interna, após os paddings, para menos de aproximadamente 1000 px. Abaixo de aproximadamente 600 px, ou quando a coluna do formulário não comportar dois campos legíveis, SHALL organizar os campos em uma coluna.

#### Scenario: Perfil em desktop amplo
- **WHEN** o perfil é exibido em viewport desktop de 1366 px com a sidebar aberta e espaço restante suficiente
- **THEN** o cartão de cadastro e o cartão de pets aparecem em duas colunas, com o formulário organizado em duas colunas e sem rolagem horizontal

#### Scenario: Sidebar reduz a área disponível
- **WHEN** a viewport ou o estado da sidebar deixa espaço insuficiente para manter ambos os cartões legíveis lado a lado
- **THEN** os cartões empilham sem sobreposição, cortes ou rolagem horizontal

#### Scenario: Perfil em viewport estreita
- **WHEN** o perfil é exibido abaixo dos pontos de adaptação definidos
- **THEN** os campos do formulário se organizam em uma coluna quando necessário e todos os controles permanecem acessíveis

### Requirement: Formulário existente mantém o contrato e os feedbacks do cadastro
O sistema SHALL preservar o contrato atual com o Xano, incluindo nomes de campos, validações, seleção de espécie e raça, upload opcional da foto, mensagens de estado e atualização da lista após cadastro. Todos os campos SHALL ter identificação visível e controles com a mesma altura e acabamento. Os campos SHALL usar espaçamento uniforme de aproximadamente 16 px entre linhas e colunas e altura de aproximadamente 48 px. A área de seleção de foto SHALL ter borda tracejada verde de 1,5–2 px, cantos arredondados e altura aproximada de 140–150 px; depois da seleção, SHALL mostrar um preview local sem iniciar um envio ao servidor antes do cadastro.

#### Scenario: Campos apresentam rótulos e dimensões consistentes
- **WHEN** o tutor visualiza o formulário vazio ou preenchido
- **THEN** todos os campos, incluindo raça e data de nascimento, têm rótulos legíveis, controles com aproximadamente 48 px de altura e o mesmo espaçamento vertical e horizontal de aproximadamente 16 px

#### Scenario: Área de upload apresenta dimensão e contraste definidos
- **WHEN** o tutor visualiza a área de seleção de foto antes de escolher um arquivo
- **THEN** a área tem entre 140 e 150 px de altura, borda tracejada verde de 1,5–2 px e cantos arredondados

#### Scenario: Tutor seleciona uma foto antes de cadastrar
- **WHEN** o tutor escolhe uma imagem válida no campo de foto
- **THEN** o formulário exibe o preview local da imagem sem alterar os dados enviados nem iniciar um upload ao servidor antes do envio do cadastro

#### Scenario: Tutor cadastra pet com foto
- **WHEN** o tutor envia o formulário válido com uma foto selecionada
- **THEN** o evento existente envia os mesmos campos e a foto ao Xano, apresenta o feedback real da operação e atualiza a lista

#### Scenario: Tutor cadastra pet sem foto
- **WHEN** o tutor envia o formulário válido sem uma foto selecionada
- **THEN** o cadastro continua usando o fluxo existente sem exigir foto e a listagem atualizada usa a patinha como fallback

### Requirement: Mascote decorativo não prejudica a interação
O sistema SHALL apresentar a tartaruga na pose com os dois braços levantados, usando imagem com transparência real, centralizada na coluna direita abaixo do cartão “Meus pets” e encostada à borda inferior da viewport. A imagem SHALL ter largura aproximada de 200–220 px e integrar o fluxo da coluna para descer junto com o cartão se a lista crescer, sem sobrepor conteúdo. SHALL manter o elemento decorativo sem interceptar eventos de ponteiro. SHALL ocultá-lo quando as colunas empilharem, quando a viewport ficar abaixo de aproximadamente 1100 px ou a largura interna após os paddings ficar abaixo de aproximadamente 1000 px ou quando houver risco de sobreposição.

#### Scenario: Mascote em viewport ampla
- **WHEN** o perfil é exibido em viewport ampla com espaço livre abaixo do cartão de pets
- **THEN** o mascote aparece com transparência real, centralizado abaixo do cartão na coluna direita e com a base junto à borda inferior da viewport, podendo ser cortado somente por essa borda
- **AND** não encobre nem bloqueia controles e não intercepta eventos de ponteiro

#### Scenario: Lista de pets cresce
- **WHEN** a lista de pets aumenta de altura
- **THEN** o mascote permanece depois do cartão no fluxo da coluna e desce com ele, sem sobreposição

#### Scenario: Mascote em tela pequena
- **WHEN** a viewport fica abaixo de aproximadamente 1100 px ou a largura interna da área de conteúdo fica abaixo de aproximadamente 1000 px ou não comporta o mascote sem sobrepor conteúdo
- **THEN** o mascote fica oculto e todos os controles permanecem acessíveis
