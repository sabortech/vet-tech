## MODIFIED Requirements

### Requirement: Formulário existente mantém o contrato e os feedbacks do cadastro
O sistema SHALL preservar o contrato com o Xano, incluindo nomes de campos, validações, seleção de espécie e raça, foto opcional, mensagens de estado e atualização da lista após cadastro. A foto selecionada SHALL ser convertida em data URI base64 e enviada no campo `foto` do mesmo JSON do cadastro, com tamanho máximo de 1 MB no arquivo original. Todos os campos SHALL ter identificação visível e controles com a mesma altura e acabamento. Os campos SHALL usar espaçamento uniforme de aproximadamente 16 px entre linhas e colunas e altura de aproximadamente 48 px. A área de seleção de foto SHALL ter borda tracejada verde de 1,5–2 px, cantos arredondados e altura aproximada de 140–150 px; depois da seleção, SHALL mostrar um preview local sem iniciar um envio ao servidor antes do cadastro.

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
- **THEN** o evento existente envia os mesmos campos em JSON com a foto em data URI base64 no campo `foto`, apresenta o feedback real da operação e atualiza a lista

#### Scenario: Tutor cadastra pet sem foto
- **WHEN** o tutor envia o formulário válido sem uma foto selecionada
- **THEN** o cadastro continua usando o fluxo existente sem exigir foto e a listagem atualizada usa a patinha como fallback

#### Scenario: Foto acima do limite
- **WHEN** o tutor tenta selecionar uma imagem maior que 1 MB
- **THEN** a área de upload não aceita o arquivo e o cadastro não envia foto

### Requirement: Lista mostra foto disponível e dados legíveis do pet
O sistema SHALL exibir cada pet com avatar circular, usando sua foto quando disponível e uma patinha como fallback. SHALL considerar disponível somente foto em URL `http(s)://` ou data URI `data:image/`. SHALL exibir nome, espécie, raça, sexo e data sem criar separadores soltos para valores opcionais; datas válidas SHALL usar o formato dd/mm/aaaa e variações conhecidas de sexo SHALL ser apresentadas como “Macho” ou “Fêmea” sem modificar o valor persistido.

#### Scenario: Pet possui foto e dados preenchidos
- **WHEN** a listagem contém foto, data válida e uma variação conhecida do valor de sexo
- **THEN** o perfil exibe a foto no avatar, formata a data como dd/mm/aaaa e normaliza somente a apresentação do sexo

#### Scenario: Pet possui foto armazenada em base64
- **WHEN** a listagem contém um pet cuja foto é um data URI `data:image/`
- **THEN** o perfil e o dashboard exibem essa foto no avatar

#### Scenario: Pet não possui foto ou dado opcional
- **WHEN** a listagem contém um pet sem foto, com foto em formato não reconhecido ou sem um ou mais dados opcionais
- **THEN** o avatar usa a patinha e a descrição não apresenta separadores órfãos nem valores fabricados

#### Scenario: Sexo desconhecido ou data inválida
- **WHEN** o valor de sexo não corresponde a uma variação conhecida ou a data não pode ser interpretada com segurança
- **THEN** o perfil preserva o texto recebido para o sexo e não apresenta uma data incorretamente reformatada
