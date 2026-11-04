## ADDED Requirements

### Requirement: Foto preenche a moldura circular no histórico anterior
O retrato do pet no histórico anterior SHALL preencher a área interna da moldura com recorte circular, centralizado e proporcional, sem folga interna ou deformação. SHALL manter largura externa de 120 px em desktop e 110 px em celular, com altura igual à largura, preservando borda, sombra, informações, controles e indicações de ausência/erro. SHALL preservar as regras existentes de autorização e carregamento.

#### Scenario: Abrir histórico com foto
- **WHEN** o usuário abre um histórico autorizado com foto horizontal, vertical ou quadrada em tema claro ou escuro, no desktop ou celular
- **THEN** a foto cobre o interior do círculo sem distorção e o painel continua permitindo navegar entre categorias e fechar

### Requirement: Foto preenche a moldura circular em Horários
A foto carregada do pet em Horários SHALL preencher toda a área interna da moldura circular, centralizada, com proporção preservada e recorte das sobras, sem faixa interna de espaçamento. SHALL manter o tamanho externo da moldura, a estrutura do card e os controles existentes. O LED e seu halo SHALL continuar circulando na borda no sentido horário com a cor do status, desacelerando com movimento reduzido. O recorte da imagem SHALL NOT cortar o halo externo ou interceptar cliques. Fotos ausentes, falhas de carregamento e acesso revogado SHALL conservar suas indicações existentes; avatares de outras telas SHALL permanecer iguais.

#### Scenario: Fotos com proporções diferentes
- **WHEN** o card autorizado carrega uma foto horizontal, vertical ou quadrada em desktop ou celular
- **THEN** a imagem cobre a área interna circular sem distorção ou folga entre foto e moldura, preservando dimensões e ações do card

#### Scenario: LED preservado em temas e estados
- **WHEN** Horários mostra consultas agendadas, em atendimento e finalizadas nos temas claro e escuro, inclusive com movimento reduzido
- **THEN** o LED vermelho, amarelo ou verde e seu halo percorrem a borda continuamente no sentido horário, mais lentamente com movimento reduzido, sem mover a foto nem bloquear controles

#### Scenario: Ausência, erro e acesso revogado
- **GIVEN** um card sem foto, com foto que falhou ao carregar ou com autorização revogada
- **WHEN** a agenda apresenta o card
- **THEN** mantém respectivamente a indicação de foto ausente, de foto indisponível ou de acesso revogado, sem expor dados privados bloqueados nem alterar o fluxo das ações permitidas
