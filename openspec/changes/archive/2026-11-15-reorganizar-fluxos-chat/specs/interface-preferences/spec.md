## MODIFIED Requirements

### Requirement: Borda luminosa global do assistente
O sistema SHALL apresentar um segmento verde luminoso com halo percorrendo suavemente o perímetro externo na janela aberta do assistente. O percurso SHALL acompanhar os cantos da janela, sem atravessar cabeçalho, banner ou conteúdo, inclusive quando o banner estiver oculto. SHALL manter ciclo linear contínuo de 6s, ou 12s em movimento reduzido. O efeito SHALL funcionar para visitantes, tutores e veterinários, nos dois temas e em desktop/celular, adaptando-se ao tamanho real do painel. SHALL NOT interceptar cliques, foco, mensagens ou histórico. Ao fechar/minimizar SHALL deixar de animar.

#### Scenario: Abrir em qualquer perfil
- **WHEN** visitante, tutor ou veterinário abre o assistente em uma tela disponível
- **THEN** o mesmo efeito percorre a borda externa, e os controles da conversa continuam funcionais

#### Scenario: Tema e tamanho da janela
- **WHEN** o tema muda ou o chat é aberto no celular
- **THEN** o traço mantém o movimento e acompanha o perímetro externo sem cobrir conteúdo nem criar overflow

#### Scenario: Minimizar e reabrir
- **WHEN** o chat é minimizado e reaberto
- **THEN** o efeito para enquanto fechado e volta a circular quando a janela é exibida

#### Scenario: Percorrer a divisória
- **WHEN** o chat está aberto
- **THEN** o segmento percorre somente a borda externa nos modos assistente, encaminhamento, lista e atendimento, sem saltos de posição

#### Scenario: Redimensionar o chat
- **WHEN** a janela ou altura do banner muda
- **THEN** o caminho mantém as curvas externas alinhadas com o painel sem invadir texto e controles

#### Scenario: Tema e movimento reduzido
- **WHEN** o usuário alterna o tema ou solicita movimento reduzido
- **THEN** o halo acompanha o segmento nos dois temas e a circulação continua em 12s quando o movimento é reduzido
