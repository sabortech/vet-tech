# Spec Delta

## Purpose

Define a apresentação responsiva do perfil autenticado do tutor e dos pets associados, preservando os fluxos de cadastro, consulta, envio de foto e saída já existentes. A capacidade mantém o perfil na rota atual e deixa os dados pessoais e dos animais protegidos pela autenticação existente.

## ADDED Requirements

### Requirement: Perfil do tutor é remodelado na rota autenticada existente
O sistema SHALL apresentar o perfil do tutor autenticado na rota atual, sem criar outra página ou rota. A tela SHALL conter o título “Perfil do tutor”, o botão “Sair”, os cartões “Cadastrar pet” e “Meus pets” e SHALL preservar os textos, nomes de campos e ações existentes do cadastro, da atualização da lista e da saída.

#### Scenario: Tutor autenticado acessa o perfil
- **WHEN** um tutor autenticado acessa o perfil
- **THEN** a tela remodelada aparece na rota atual com o cadastro e a lista de pets lado a lado em desktop e sem alterar os textos e ações existentes

#### Scenario: Tutor encerra a sessão pelo perfil
- **WHEN** o tutor aciona “Sair”
- **THEN** o fluxo de logout existente é executado e o acesso ao perfil continua protegido pela autenticação

### Requirement: Perfil e formulário adaptam-se à largura disponível
O sistema SHALL manter o formulário e a lista utilizáveis sem rolagem horizontal. Em larguras menores que aproximadamente 1100 px, ou quando o espaço restante não comportar os dois cartões, SHALL empilhar os cartões; abaixo de aproximadamente 600 px, SHALL organizar os campos do formulário em uma coluna.

#### Scenario: Perfil em desktop amplo
- **WHEN** o perfil é exibido em viewport desktop com espaço suficiente
- **THEN** o cartão de cadastro e o cartão de pets aparecem em duas colunas, com o formulário organizado em duas colunas

#### Scenario: Perfil em viewport estreita
- **WHEN** o perfil é exibido em viewport abaixo dos pontos de adaptação definidos
- **THEN** os cartões e campos se empilham conforme necessário, sem cortar controles ou produzir rolagem horizontal

### Requirement: Lista mostra foto disponível e dados legíveis do pet
O sistema SHALL exibir cada pet com avatar circular, usando sua foto quando disponível e uma patinha como fallback. SHALL exibir nome, espécie, raça, sexo e data sem criar separadores soltos para valores opcionais; datas válidas SHALL usar o formato dd/mm/aaaa e variações conhecidas de sexo SHALL ser apresentadas como “Macho” ou “Fêmea” sem modificar o valor persistido.

#### Scenario: Pet possui foto e dados preenchidos
- **WHEN** a listagem contém foto, data válida e uma variação conhecida do valor de sexo
- **THEN** o perfil exibe a foto no avatar, formata a data como dd/mm/aaaa e normaliza somente a apresentação do sexo

#### Scenario: Pet não possui foto ou dado opcional
- **WHEN** a listagem contém um pet sem foto ou sem um ou mais dados opcionais
- **THEN** o avatar usa a patinha e a descrição não apresenta separadores órfãos nem valores fabricados

#### Scenario: Sexo desconhecido ou data inválida
- **WHEN** o valor de sexo não corresponde a uma variação conhecida ou a data não pode ser interpretada com segurança
- **THEN** o perfil preserva o texto recebido para o sexo e não apresenta uma data incorretamente reformatada

### Requirement: Formulário existente mantém o contrato e os feedbacks do cadastro
O sistema SHALL preservar o contrato atual com o Xano, incluindo nomes de campos, validações, seleção de espécie e raça, upload opcional da foto, mensagens de estado e atualização da lista após cadastro.

#### Scenario: Tutor cadastra pet com foto
- **WHEN** o tutor envia o formulário válido com uma foto selecionada
- **THEN** o evento existente envia os mesmos campos e a foto ao Xano, apresenta o feedback real da operação e atualiza a lista

#### Scenario: Tutor cadastra pet sem foto
- **WHEN** o tutor envia o formulário válido sem uma foto selecionada
- **THEN** o cadastro continua usando o fluxo existente sem exigir foto e a listagem atualizada usa a patinha como fallback

### Requirement: Mascote decorativo não prejudica a interação
O sistema SHALL apresentar a tartaruga como elemento decorativo no canto inferior direito em telas que disponham de espaço, sem interceptar eventos de ponteiro nem cobrir campos ou ações. Em telas pequenas, SHALL ocultar o elemento.

#### Scenario: Mascote em viewport ampla
- **WHEN** o perfil é exibido em viewport ampla
- **THEN** o mascote é parcialmente recortado pela borda inferior direita e não encobre nem bloqueia controles

#### Scenario: Mascote em tela pequena
- **WHEN** o perfil é exibido em viewport pequena
- **THEN** o mascote não é mostrado e todos os controles permanecem acessíveis
