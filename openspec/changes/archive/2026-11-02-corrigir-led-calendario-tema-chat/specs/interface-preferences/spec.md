## MODIFIED Requirements

### Requirement: Tema é coerente em todo o sistema
O sistema SHALL oferecer claro e escuro para Configurações, Meus Pets, login e cadastro, incluindo a cor da sidebar, cartões, campos, seletores, mensagens, diálogos, chat flutuante global e estados de foco e desabilitado. SHALL preservar Nunito, hierarquia, dimensões e identidade verde. Login e cadastro SHALL seguir a preferência de tema, preservando sua estrutura, imagens e identidade visual.

#### Scenario: Navegação no modo escuro
- **WHEN** o tutor ativa Modo escuro e navega entre Configurações e Meus Pets
- **THEN** ambas as telas usam o mesmo tema, sem superfícies claras residuais ou texto ilegível

#### Scenario: Saída da área autenticada
- **WHEN** a sessão termina e a pessoa visualiza login ou cadastro
- **THEN** essas telas continuam usando o tema escolhido e preservam sua estrutura e identidade visual

#### Scenario: Chat acompanha a preferência em todos os perfis
- **WHEN** visitante, tutor ou veterinário abre o assistente com tema claro ou escuro, ou a preferência muda enquanto o chat está aberto
- **THEN** painel, mensagens, campo de texto, ações e histórico acompanham imediatamente a mesma preferência sem reiniciar a conversa
