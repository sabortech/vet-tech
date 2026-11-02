# Preferências de interface

## Purpose

Permitir que a pessoa escolha o tema da interface inteira e a expansão do menu, com aplicação imediata e persistência local sem armazenar informações pessoais da conta.

## Requirements

### Requirement: Preferências oferecem aparência e navegação
O sistema SHALL apresentar na aba Preferências um cartão Aparência com o controle Modo escuro e um cartão Navegação com Manter o menu lateral expandido. Ambos SHALL usar o mesmo estilo de switch, com dimensões, cores e foco consistentes, e refletir o estado efetivo e aplicar alterações imediatamente, sem botão de salvamento, com descrição de persistência neste navegador.

#### Scenario: Alternância de preferência
- **WHEN** o tutor altera um dos controles
- **THEN** a interface reflete a escolha imediatamente e apresenta confirmação discreta sem depender da API Xano

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

### Requirement: Preferências são locais e carregam sem flash de tema incorreto
O sistema SHALL lembrar tema e expansão neste navegador, sem gravar token, dados pessoais ou senhas nesse mecanismo. Sem preferência de tema válida SHALL usar claro; sem preferência válida de expansão SHALL manter o padrão expandido. O tema salvo SHALL ser aplicado antes da apresentação visível de qualquer tela, sem mostrar brevemente o tema oposto. Se o armazenamento estiver indisponível, a interface SHALL continuar utilizável com preferência em memória durante a página atual.

#### Scenario: Preferência salva é retomada
- **GIVEN** há preferência escura salva neste navegador
- **WHEN** qualquer tela é apresentada novamente
- **THEN** seu primeiro conteúdo visível já usa o tema escuro
- **AND** a preferência não cria nem restaura uma sessão autenticada

#### Scenario: Armazenamento indisponível ou valor inválido
- **WHEN** o armazenamento local não pode ser usado ou contém valor desconhecido
- **THEN** a tela permanece utilizável, usa o padrão no caso de valor inválido e não promete sincronização entre dispositivos

### Requirement: Preferência do menu reutiliza o estado compartilhado
O controle de expansão SHALL compartilhar o estado existente com o botão da sidebar e manter a escolha entre páginas e abas do mesmo navegador. Em celular, SHALL preservar o comportamento atual de gaveta fechada por padrão, independentemente da preferência desktop.

#### Scenario: Controle e sidebar sincronizados
- **WHEN** o tutor recolhe ou expande a sidebar por qualquer um dos dois controles
- **THEN** o outro controle reflete o mesmo estado sem preferência concorrente

#### Scenario: Celular preserva gaveta
- **GIVEN** há preferência desktop expandida
- **WHEN** a tela é usada abaixo de 768 px
- **THEN** o menu continua em gaveta inicialmente fechada e pode ser aberto e fechado normalmente

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
