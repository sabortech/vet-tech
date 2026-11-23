# assistant-chat-banner Specification

## Purpose
Apresentar a animação da tartaruga no topo do assistente, de forma contínua e consistente entre telas e perfis.

## Requirements

### Requirement: Banner animado do assistente
O chat compartilhado SHALL apresentar gifturtle.mp4 abaixo do cabeçalho e antes da primeira mensagem, ocupando toda a largura do painel na proporção original 16:9, sem recorte, reprodução automática silenciosa, inline e em loop. Após o tutor enviar a primeira mensagem ao assistente, o banner SHALL ficar oculto até o início de uma nova conversa. O vídeo SHALL pausar quando o chat estiver fechado, no histórico ou nos fluxos humanos e retomar ao retornar ao assistente somente se ainda não houve envio na conversa atual.

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
- **WHEN** a pessoa rola a conversa do assistente
- **THEN** o banner permanece fixo abaixo do cabeçalho e da navegação, fora da área de rolagem

#### Scenario: Encaminhamento e histórico
- **WHEN** a pessoa abre confirmação, lista, atendimento humano ou histórico
- **THEN** o banner fica oculto e pausado para dar espaço ao conteúdo

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
