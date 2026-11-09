# Spec Delta

## MODIFIED Requirements

### Requirement: Cards de Horários com paleta do atendimento
Cards de Horários SHALL compartilhar a paleta de Consultas: vermelho/agendada, amarelo/em atendimento, verde/finalizada, incluindo nome, ícones, badge, botões, fundo, bordas e foco. O cartão completo SHALL apresentar um segmento luminoso circulando continuamente no sentido horário pelo seu perímetro, com cor e halo do status. O contorno SHALL acompanhar altura e largura do cartão, inclusive após reorganização de ações no celular, sem interceptar cliques. O LED circular da foto SHALL usar a cor e halo do status, mantendo movimento horário e desaceleração com movimento reduzido. O LED do cartão SHALL também desacelerar com movimento reduzido. Estados cancelados ou desconhecidos SHALL NOT receber o LED de perímetro. Ações, autorização e dados da agenda SHALL ser preservados.

#### Scenario: Horários com estados diferentes
- **WHEN** a agenda mostra consultas agendadas, em atendimento e concluídas
- **THEN** seus cards usam vermelho, amarelo e verde respectivamente em ambos os temas, com controles legíveis e funcionais

#### Scenario: Segmento circula no cartão completo
- **WHEN** o médico observa um cartão em estado agendada, em atendimento ou finalizada
- **THEN** o segmento e seu halo percorrem o contorno completo continuamente na cor correspondente, preservando foto e ações

#### Scenario: Celular e movimento reduzido
- **WHEN** o cartão muda de tamanho ou o usuário solicita movimento reduzido
- **THEN** o LED permanece ajustado ao perímetro e continua circulando mais lentamente, sem provocar rolagem horizontal ou bloquear os botões

#### Scenario: Estado sem paleta clínica ativa
- **WHEN** um cartão está cancelado ou possui estado desconhecido
- **THEN** o LED de perímetro não aparece e a apresentação neutra permanece
