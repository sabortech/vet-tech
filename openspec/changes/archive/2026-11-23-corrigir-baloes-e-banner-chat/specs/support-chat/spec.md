# Spec Delta

## MODIFIED Requirements

### Requirement: Paleta completa do atendimento
Durante conversa humana, cabeçalho, navegação, botões, ícones, foco, campo e balões SHALL acompanhar a paleta do status, com vermelho aguardando, amarelo em atendimento e verde encerrado. Balões de mensagens enviadas SHALL ter fundo sólido e opaco, distinguível do fundo da conversa nos temas claro e escuro. O texto SHALL manter contraste legível nos temas claro/escuro. Fora do ticket, o chat SHALL restaurar a paleta verde padrão sem alterar o tema da página.

#### Scenario: Atendimento em andamento
- **WHEN** o usuário visualiza atendimento em andamento
- **THEN** cabeçalho e envio usam amarelo com texto escuro e os demais elementos usam tons contextuais, sem persistir verde das ações do assistente

#### Scenario: Balão enviado em atendimento humano
- **WHEN** tutor ou veterinário visualiza uma mensagem própria em um atendimento
- **THEN** o balão tem preenchimento opaco e é visualmente distinguível do fundo nos temas claro e escuro, mantendo a cor correspondente ao status

## ADDED Requirements

### Requirement: Recibo de leitura das mensagens ao assistente
Mensagens enviadas ao assistente SHALL mostrar Entregue enquanto aguardam resposta e mudar para Visto quando uma resposta válida do bot chegar. Uma falha ou timeout SHALL manter Entregue.

#### Scenario: Bot responde
- **WHEN** o bot responde com sucesso à mensagem enviada
- **THEN** a mensagem do tutor muda de Entregue para Visto

#### Scenario: Resposta falha ou demora
- **WHEN** ocorre falha ou timeout antes de uma resposta válida do bot
- **THEN** a mensagem permanece como Entregue
