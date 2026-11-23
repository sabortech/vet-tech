# Spec Delta

## ADDED Requirements

### Requirement: Banner oculto após a primeira mensagem
Após o tutor enviar a primeira mensagem ao assistente, o banner de vídeo SHALL ficar oculto até o início de uma nova conversa.

#### Scenario: Primeira mensagem enviada ao assistente
- **WHEN** o tutor envia uma mensagem ao assistente
- **THEN** o vídeo é pausado e o banner fica oculto durante o restante da conversa

#### Scenario: Retornar do histórico
- **GIVEN** o tutor já enviou uma mensagem na conversa atual
- **WHEN** retorna do histórico para essa conversa
- **THEN** o banner permanece oculto

#### Scenario: Nova conversa com o assistente
- **WHEN** o tutor inicia uma nova conversa com o assistente
- **THEN** o banner reaparece antes da saudação e o vídeo pode reproduzir
