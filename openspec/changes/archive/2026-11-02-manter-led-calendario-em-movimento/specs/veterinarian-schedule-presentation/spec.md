## MODIFIED Requirements

### Requirement: Luz verde apenas na janela aberta
O sistema SHALL apresentar um brilho verde animado percorrendo somente as bordas da janela aberta no sentido horário. Hoje e o ícone de calendário SHALL NOT receber esse efeito. A animação SHALL ser contínua, linear e suave, sem bloquear conteúdo ou cliques. Quando houver preferência por movimento reduzido, SHALL usar velocidade menor mantendo o traço em circulação conforme solicitado pelo usuário.

#### Scenario: Janela aberta
- **WHEN** o calendário está aberto
- **THEN** a borda da janela mostra a luz verde no sentido horário e seus controles permanecem utilizáveis

#### Scenario: Movimento reduzido
- **WHEN** o navegador solicita movimento reduzido
- **THEN** o segmento continua circulando no sentido horário em velocidade menor, sem transformar toda a borda em luz estática
