# Spec Delta

## Purpose

Agradecer pelo novo cadastro no Vet Tech e orientar tutores e veterinários conforme seu perfil, com mensagem acessível e envio transacional controlado pelo backend.

## ADDED Requirements

### Requirement: Boas-vindas decorrem de cadastro confirmado
O sistema SHALL iniciar uma tentativa de envio de boas-vindas após persistir com sucesso um novo cadastro de tutor ou veterinário, inclusive por chamada direta ao backend. SHALL usar o nome, e-mail e perfil da identidade criada. Cadastro rejeitado, rollback, login normal, login Google e redefinição de senha SHALL NOT gerar boas-vindas. A mensagem SHALL NOT verificar a posse do e-mail nem autenticar o destinatário.

#### Scenario: Novo tutor
- **WHEN** o cadastro de tutor é concluído
- **THEN** a tentativa de boas-vindas usa o destinatário e o perfil tutor persistidos

#### Scenario: Novo veterinário
- **WHEN** o cadastro veterinário e seus vínculos obrigatórios são concluídos
- **THEN** a tentativa usa o destinatário e o perfil veterinário persistidos

#### Scenario: Cadastro não confirmado
- **WHEN** validação, duplicidade ou transação impede a criação da conta
- **THEN** nenhuma mensagem de boas-vindas é enviada

#### Scenario: Outro fluxo de autenticação
- **WHEN** uma conta existente entra com senha ou Google ou altera sua senha
- **THEN** não recebe nova mensagem de boas-vindas

### Requirement: Conteúdo distingue os dois perfis
O e-mail SHALL usar português brasileiro, marca Vet Tech e saudação com nome escapado. SHALL agradecer o cadastro e orientar tutores sobre cadastrar pets e acompanhar informações registradas; para veterinários SHALL orientar agenda e atendimentos com acesso ao prontuário condicionado à autorização do tutor. SHALL NOT apresentar PetSync, título em inglês, campos simulados De/Para/Assunto, dados fictícios de suporte ou funcionalidades inexistentes.

#### Scenario: Mesmo identificador em dois perfis
- **GIVEN** contas de tutor e veterinário com IDs numéricos coincidentes
- **WHEN** os e-mails são preparados
- **THEN** cada mensagem usa a identidade, nome, destinatário e orientações de seu próprio perfil

#### Scenario: Nome contém caracteres especiais
- **WHEN** o nome cadastrado contém acentos ou caracteres de HTML
- **THEN** o nome é apresentado como texto, sem execução ou inserção de marcação arbitrária

### Requirement: Template mantém a identidade visual aprovada
A mensagem SHALL apresentar cartão responsivo com a imagem original `clinicturtle.jpeg` no corpo, proporção preservada, sem anexos; títulos verdes, agradecimento e orientações legíveis. SHALL incluir Desenvolvedores do Sistema com fotos arredondadas em linha e nomes Davi Diniz, Vitor Sousa e Danikelly Alves, sem shadow boxes, e rodapé centralizado Copyright © by Vet Tech Team. SHALL oferecer HTML e texto equivalente e preservar conteúdo essencial com imagens bloqueadas.

#### Scenario: E-mail no celular
- **WHEN** a mensagem é aberta em largura de 390 px
- **THEN** texto e fotos permanecem organizados, sem rolagem horizontal nem conteúdo essencial cortado

#### Scenario: Imagens bloqueadas
- **WHEN** o cliente de e-mail não carrega as imagens
- **THEN** marca, saudação, orientações, nomes dos desenvolvedores e copyright continuam legíveis

### Requirement: Botão de acesso usa a URL temporária autorizada
O e-mail SHALL incluir o botão Acesse nosso sistema e o equivalente textual, apontando temporariamente para http://localhost:3000/login conforme autorização explícita do usuário. A URL SHALL ser configurável no template, sem aceitar esquema executável ou credenciais no endereço. A restrição de que localhost somente acessa o aparelho do destinatário SHALL ser documentada; um endereço público HTTPS poderá substituir a configuração quando disponível.

#### Scenario: Boas-vindas para qualquer perfil
- **WHEN** a mensagem de tutor ou veterinário é aberta
- **THEN** o botão é legível e aponta para a URL local autorizada, e a versão textual informa o mesmo destino

### Requirement: Envio é privado e não desfaz cadastro
O backend SHALL enviar pelo provedor transacional já configurado, com credenciais privadas, sem endpoint público de envio arbitrário. Uma falha, bloqueio, timeout ou cota excedida do provedor SHALL NOT desfazer o cadastro ou transformar uma conta criada em erro de cadastro. Aceitação SHALL NOT ser apresentada como garantia de entrega. Senha, CPF, CRMV, tokens e dados clínicos SHALL NOT aparecer na mensagem ou nos registros operacionais.

#### Scenario: Provedor indisponível
- **GIVEN** a conta já foi criada
- **WHEN** o envio é recusado ou expira
- **THEN** o cadastro continua confirmado, o login permanece possível e a falha de entrega fica registrada sem credenciais

### Requirement: Tentativas não duplicam boas-vindas
O sistema SHALL registrar evento único por perfil e identidade e reservar atomicamente uma única tentativa por evento, inclusive diante de concorrência. SHALL NOT gerar mensagens duplicadas ao repetir cadastro rejeitado ou processamento interno. Timeout ou resultado incerto SHALL NOT causar reenvio automático. Contas antigas SHALL NOT receber disparo em massa por esta entrega.

#### Scenario: Duas tentativas disputam o mesmo evento
- **WHEN** processamentos concorrentes tentam enviar boas-vindas da mesma conta
- **THEN** no máximo um realiza a chamada ao provedor

#### Scenario: Resposta do envio não chega
- **WHEN** a tentativa termina sem confirmação do resultado
- **THEN** o sistema registra resultado incerto sem repetir automaticamente nem pedir que a pessoa recrie a conta

### Requirement: Fundo e cabeçalho refletem a revisão visual aprovada
O e-mail SHALL usar a arte fundo.webp como cenário externo, com fallback de cor, e cabeçalho verde-oliva coordenado ao cenário. A tartaruga em V SHALL aparecer à esquerda da marca Vet Tech com proporção preservada, sem halo claro externo e com a base visível apoiada na divisória inferior do cabeçalho. As imagens SHALL ser HTTPS sem anexos, com texto alternativo e legibilidade da marca e do rodapé mesmo com imagens bloqueadas.

#### Scenario: Abrir boas-vindas de qualquer perfil
- **WHEN** o destinatário abre a mensagem de tutor ou veterinário
- **THEN** vê o cenário externo, o cabeçalho coordenado e a mascote à esquerda sem sobreposição ou rolagem horizontal
