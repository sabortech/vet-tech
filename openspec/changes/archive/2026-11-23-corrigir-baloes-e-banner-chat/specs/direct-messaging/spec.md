# Spec Delta

## MODIFIED Requirements

### Requirement: Compositor compartilhado e alterações seguras
Conversas simples SHALL reutilizar emojis, nomes por participante, recibos Entregue/Visto e menu de edição/exclusão próprias em até 10 minutos do envio original, com autoria, revisão, retry idempotente e auditoria privada no backend. Balões de mensagens enviadas SHALL ter fundo sólido e opaco, distinguível do fundo da conversa nos temas claro e escuro. Não SHALL apresentar assunção, encerramento ou status de atendimento. A conversa SHALL persistir ao fechar e reabrir.

#### Scenario: Mensagem e reabertura
- **WHEN** um participante envia mensagem e reabre a conversa
- **THEN** o texto persistido continua no histórico com recibos e regras de alteração preservados

#### Scenario: Balão de mensagem direta enviada
- **WHEN** tutor ou veterinário visualiza uma mensagem própria em uma conversa privada
- **THEN** o balão tem preenchimento opaco e é visualmente distinguível do fundo nos temas claro e escuro
