## ADDED Requirements

### Requirement: Borda luminosa global do assistente
O sistema SHALL apresentar um segmento verde luminoso percorrendo suavemente o perímetro da janela aberta do assistente no sentido horário, com ciclo linear contínuo de 6s. Em movimento reduzido SHALL usar 12s mantendo circulação. O efeito SHALL funcionar para visitantes, tutores e veterinários em qualquer tela e nos temas claro/escuro, adaptar-se ao desktop e celular e não interceptar cliques, foco, mensagens ou histórico. Ao fechar/minimizar a janela SHALL deixar de animar.

#### Scenario: Abrir em qualquer perfil
- **WHEN** visitante, tutor ou veterinário abre o assistente em uma tela disponível
- **THEN** o mesmo efeito contorna a janela e os controles da conversa continuam funcionais

#### Scenario: Tema e tamanho da janela
- **WHEN** o tema muda ou o chat é aberto no celular
- **THEN** o traço mantém o movimento e acompanha o perímetro sem cobrir conteúdo nem criar overflow

#### Scenario: Minimizar e reabrir
- **WHEN** o chat é minimizado e reaberto
- **THEN** o efeito para enquanto fechado e volta a circular quando a janela é exibida
