## MODIFIED Requirements


### Requirement: Banner animado do assistente
O chat compartilhado SHALL apresentar gifturtle.mp4 abaixo do cabeçalho e antes da primeira mensagem, ocupando toda a largura do painel na proporção original 16:9, sem recorte, reprodução automática silenciosa, inline e em loop. O vídeo SHALL pausar quando o chat estiver fechado, no histórico ou nos fluxos humanos e retomar ao retornar ao assistente.

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
