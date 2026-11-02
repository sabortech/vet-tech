# Spec Delta

## Purpose

Apresentar a animação da tartaruga no topo do assistente, de forma contínua e consistente entre telas e perfis.

## ADDED Requirements

### Requirement: Banner animado do assistente
O chat compartilhado SHALL apresentar gifturtle.mp4 abaixo do cabeçalho e antes da primeira mensagem, com proporção preservada, reprodução automática silenciosa, inline e em loop. O vídeo SHALL pausar quando o chat estiver fechado e retomar ao abrir.

#### Scenario: Abrir o chat
- **WHEN** uma pessoa de qualquer perfil abre o assistente
- **THEN** o banner aparece antes da saudação e reproduz sem som, repetindo ao final

#### Scenario: Fechar e reabrir
- **WHEN** a pessoa fecha e depois reabre o chat
- **THEN** o vídeo pausa enquanto fechado e volta a reproduzir no painel aberto

#### Scenario: Temas e celular
- **WHEN** o chat é usado nos temas claro ou escuro e em tela pequena
- **THEN** o banner respeita a largura do painel e mantém mensagens e envio acessíveis

#### Scenario: Rolar mensagens
- **WHEN** a pessoa rola a conversa ou consulta o histórico
- **THEN** o banner permanece fixo abaixo do cabeçalho, fora da área de rolagem
