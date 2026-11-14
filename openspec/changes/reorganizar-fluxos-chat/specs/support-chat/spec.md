## ADDED Requirements

### Requirement: Encaminhamento isolado e legível
O chat SHALL separar assistente, confirmação, lista e atendimento; cabeçalho e controles SHALL caber sem sobreposição em celular e desktop nos dois temas. Os botões Atendimentos e Nova conversa SHALL integrar visualmente o cabeçalho, compartilhando seu fundo verde e sem faixa ou divisória intermediária. O LED SHALL acompanhar somente o perímetro externo em todos os estados. Nova conversa SHALL apresentar somente seu contexto; históricos humanos SHALL ser abertos explicitamente.

#### Scenario: Encaminhar nova conversa
- **WHEN** o bot recomenda veterinário
- **THEN** aparecem título, explicação, pet, consentimento e ações organizadas, sem lista de conversas antigas

#### Scenario: Consultar atendimentos anteriores
- **WHEN** o usuário abre Atendimentos explicitamente
- **THEN** uma lista de cartões permite selecionar atendimento sem despejar eventos antigos no painel, com título à esquerda e botões compactos Atualizar atendimentos e Falar com assistente à direita na mesma linha

### Requirement: Retomada e consultas econômicas
O sistema SHALL oferecer tentativa manual com os mesmos campos e identidade da operação, sem repetir automaticamente escritas. SHALL impedir envios duplicados pendentes, evitar buscar atendimentos para apenas selecionar pet e suspender polling quando fechado, aba oculta ou atendimento encerrado. Listagens SHALL atualizar somente por ação explícita e atendimento ativo SHALL consultar no máximo uma vez a cada 20 segundos.

#### Scenario: Falha ao encaminhar
- **WHEN** a criação falha e o usuário tenta novamente
- **THEN** a mesma conversa e seleção são reenviadas com a identidade original e feedback visível

#### Scenario: Atendimento encerrado ou aba oculta
- **WHEN** o atendimento está encerrado ou a aba está oculta
- **THEN** não são feitas consultas periódicas ao Xano

#### Scenario: Configuração de encaminhamento ausente
- **WHEN** o servidor não possui a credencial privada obrigatória de criação
- **THEN** o chamado não é enviado ao Xano e aparece erro específico de indisponibilidade por configuração, sem apresentar uma tentativa como solução

### Requirement: Cores dos atendimentos do veterinário
As listas do tutor e do veterinário SHALL representar aguardando em vermelho, em atendimento em amarelo e encerrado em verde, com rótulos textuais preservados, contraste adequado nos dois temas e sem consultas adicionais para decoração.

#### Scenario: Fila e histórico do veterinário
- **WHEN** o tutor ou o veterinário visualiza cartões nos três estados
- **THEN** borda, status e ação acompanham a cor correspondente sem alterar ações ou autorização

### Requirement: Detalhes humanos em pop-up
O chat humano SHALL apresentar um ícone flutuante interno vermelho/aguardando, amarelo/em atendimento ou verde/encerrado. Ao ativá-lo SHALL abrir diálogo com pet, status, profissional quando disponível, informação da espera e ações de atualizar e encerrar/cancelar com motivo. Abrir o diálogo SHALL reutilizar os dados carregados, sem nova requisição. O diálogo SHALL fechar por controle, Escape ou clique externo e devolver foco ao ícone.

#### Scenario: Consultar detalhes sem ocupar a conversa
- **WHEN** o usuário abre o ícone de informações do ticket
- **THEN** as informações aparecem no pop-up, preservando a conversa e o rascunho do motivo enquanto o mesmo ticket estiver selecionado

### Requirement: Foto do pet nos atendimentos
As listas do tutor e veterinário e o pop-up de detalhes SHALL apresentar a foto cadastrada do pet em moldura circular, com fallback de patinha quando ausente ou inválida. A moldura SHALL acompanhar a cor do status. A API SHALL incluir fotos na consulta existente, sem request adicional por cartão, deduplicando fotos de um mesmo pet na resposta da lista. A fila veterinária SHALL expor apenas foto e identificador do pet além dos metadados operacionais existentes, sem nome do tutor ou conteúdo clínico antes da assunção.

#### Scenario: Lista e detalhes com foto
- **GIVEN** o usuário possui acesso autorizado ao atendimento ou à fila veterinária mínima
- **WHEN** carrega os atendimentos ou abre informações
- **THEN** vê a foto do pet ao lado da identificação, sem consulta individual para buscar a imagem

#### Scenario: Foto indisponível
- **WHEN** o pet não possui foto ou a imagem falha
- **THEN** aparece patinha na mesma moldura e as ações permanecem disponíveis

### Requirement: LEDs de status nos cartões e fotos
Cada cartão de atendimento e a moldura circular da foto SHALL apresentar um segmento luminoso circulando no sentido horário, vermelho/aguardando, amarelo/em atendimento e verde/encerrado. O halo SHALL acompanhar apenas o segmento móvel, sem bloquear cliques ou alterar layout. A foto no pop-up SHALL usar o mesmo efeito. Movimento reduzido SHALL desacelerar a animação, sem gerar eventos ou consultas remotas.

#### Scenario: Visualizar os três estados
- **WHEN** a lista mostra atendimentos de status diferentes
- **THEN** cada cartão e foto possui seu LED na cor correspondente, inclusive com fallback da foto

### Requirement: Identidade visual da conversa humana
Mensagens humanas SHALL usar ícones distintos de veterinário e tutor, inclusive nas mensagens próprias. A mascote SHALL identificar somente mensagens do assistente. O cabeçalho SHALL refletir o interlocutor e o status: no tutor, profissional responsável quando confirmado; no veterinário, conversa com tutor e pet de contexto. Retornar ao assistente SHALL restaurar nome e mascote originais. Fotos SHALL permanecer recortadas em círculo dentro da moldura, inclusive no pop-up.

#### Scenario: Conversa assumida
- **WHEN** o veterinário assume o atendimento
- **THEN** o cabeçalho do tutor mostra o profissional confirmado com ícone veterinário, e mensagens de cada perfil têm seu próprio ícone

#### Scenario: Voltar ao assistente
- **WHEN** o usuário inicia nova conversa com o assistente
- **THEN** o cabeçalho retorna à mascote e identidade do assistente, sem identidade humana anterior

### Requirement: LED da janela e pop-up por status
Durante atendimento humano o LED externo do chat e o LED do pop-up de informações SHALL acompanhar o status: vermelho aguardando, amarelo em atendimento e verde encerrado, incluindo o halo móvel. Retornar à lista ou ao assistente SHALL restaurar o LED verde padrão da janela.

#### Scenario: Atendimento em andamento
- **WHEN** o atendimento muda para em atendimento e o usuário abre informações
- **THEN** chat e pop-up apresentam LEDs amarelos em movimento, sem consultas adicionais para decoração

### Requirement: Paleta completa do atendimento
Durante conversa humana, cabeçalho, navegação, botões, ícones, foco, campo e balões SHALL acompanhar a paleta do status, com vermelho aguardando, amarelo em atendimento e verde encerrado. O texto SHALL manter contraste legível nos temas claro/escuro. Fora do ticket, o chat SHALL restaurar a paleta verde padrão sem alterar o tema da página.

#### Scenario: Atendimento em andamento
- **WHEN** o usuário visualiza atendimento em andamento
- **THEN** cabeçalho e envio usam amarelo com texto escuro e os demais elementos usam tons contextuais, sem persistir verde das ações do assistente

### Requirement: Seletor local de emojis
Todos os compositores do chat compartilhado SHALL oferecer botão de emoji que abre painel com busca, categorias e emojis nomeados em português. Selecionar SHALL inserir o emoji na posição do cursor ou substituir a seleção, respeitando limite de 1000 caracteres sem enviar mensagem automaticamente. O painel SHALL fechar por seleção, controle, Escape ou clique externo; Escape no painel SHALL manter o chat aberto. O controle SHALL ficar desabilitado quando o envio estiver indisponível. Painel e seleção SHALL usar apenas dados locais e acompanhar tema/status.

#### Scenario: Inserir emoji na conversa
- **WHEN** o usuário seleciona um emoji no painel
- **THEN** o emoji é inserido no rascunho e o foco volta ao campo sem requisição ao Xano ou n8n

#### Scenario: Atendimento indisponível para envio
- **WHEN** o atendimento está aguardando ou encerrado, ou há envio pendente
- **THEN** o botão fica desabilitado e não permite alterar o rascunho pelo seletor

### Requirement: Encerramento exclusivo pelo responsável
O Xano SHALL permitir encerrar atendimento em andamento somente ao veterinário atribuído ao chamado. O tutor SHALL poder apenas cancelar enquanto aguardando; após assunção SHALL manter leitura e mensagens sem encerramento. Veterinários não responsáveis SHALL ser impedidos de encerrar ou acessar conversa alheia. Validação de estado e autorização SHALL ocorrer no backend dentro da transação, inclusive em chamadas diretas e disputa entre cancelamento e assunção.

#### Scenario: Tutor tenta encerrar atendimento em andamento
- **GIVEN** o chamado está em atendimento
- **WHEN** o tutor tenta encerrá-lo inclusive por chamada direta
- **THEN** a operação é negada sem alteração do chamado ou evento de encerramento

#### Scenario: Responsável encerra
- **GIVEN** o chamado está em atendimento e o profissional é seu responsável
- **WHEN** envia encerramento com motivo
- **THEN** o chamado é encerrado com evento persistente e retry idempotente

#### Scenario: Tutor cancela antes da assunção
- **GIVEN** o tutor é dono do chamado aguardando
- **WHEN** confirma cancelamento com motivo
- **THEN** o chamado é encerrado somente se ainda aguarda, preservando proteção contra disputa com assunção

### Requirement: Nomes confirmados dos participantes
O detalhe autorizado SHALL fornecer somente o nome cadastrado do tutor e os metadados profissionais já existentes, sem acrescentar dados pessoais à fila. Cabeçalho SHALL mostrar o nome confirmado do interlocutor com fallback por perfil. Cada mensagem humana SHALL apresentar identificação Tutor/Veterinário e nome disponível acima do conjunto avatar/balão, sem prefixo no corpo. A obtenção do nome SHALL reutilizar a consulta do pet com join de tutor sem request HTTP ou consulta por mensagem.

#### Scenario: Conversa entre participantes
- **GIVEN** o backend confirmou acesso ao ticket
- **WHEN** o usuário visualiza a conversa
- **THEN** cabeçalho e rótulos usam nomes do banco, preservando o texto original das mensagens

### Requirement: Entrega e leitura entre participantes
Mensagens humanas próprias persistidas SHALL mostrar Entregue até o interlocutor confirmar visualização, quando SHALL mostrar Visto. A confirmação SHALL ser registrada pelo servidor somente para mensagens recebidas por um participante autorizado do ticket, sem aceitar marcação de mensagem própria, alheia ou futura. O navegador SHALL confirmar apenas mensagens visíveis no chat aberto e aba em foco, sem painéis sobrepostos. Confirmações SHALL ser monotônicas e reutilizar o transporte existente, agrupando a leitura com uma sincronização por lote e intervalo mínimo de cinco segundos entre lotes. Histórico anterior SHALL permanecer entregue até nova visualização, sem inventar leitura retroativa.

#### Scenario: Interlocutor visualiza mensagem
- **GIVEN** uma mensagem foi persistida e ainda não está lida
- **WHEN** o interlocutor a visualiza no chat ativo e a próxima sincronização confirma a leitura
- **THEN** o remetente vê Visto na próxima atualização

#### Scenario: Aba oculta ou acesso indevido
- **WHEN** a aba está oculta, o chat fechado ou a mensagem não está visível, ou outro usuário tenta confirmar leitura
- **THEN** não há confirmação automática de leitura dessa mensagem pelo navegador e o backend rejeita operações sem participação

### Requirement: Tutor responsável nos cartões próprios
Os cartões próprios SHALL mostrar nome do tutor confirmado pelo banco. A fila veterinária ainda não assumida SHALL continuar sem expor nome do tutor. O nome SHALL vir na consulta existente, sem requisição por cartão.

#### Scenario: Cartão em atendimento
- **GIVEN** o usuário é tutor proprietário ou veterinário atribuído ao atendimento
- **WHEN** abre a lista
- **THEN** vê o nome do tutor responsável junto da identificação do atendimento

### Requirement: Leitura ao trocar de perfil
Uma leitura observada no chat ativo SHALL ser sincronizada em lote após breve espera local e não SHALL depender de permanecer na aba até o próximo polling. Trocar de aba SHALL transmitir somente marcador já observado, sem marcar mensagens novas enquanto oculta. Retornar ao chat SHALL atualizar os recibos com limitação de frequência. O rótulo exibido SHALL ser Visto após confirmação.

#### Scenario: Ler e retornar ao remetente
- **WHEN** o destinatário visualiza a mensagem e troca de perfil antes de 20 segundos
- **THEN** a leitura é persistida e o remetente obtém Visto ao retornar à conversa

### Requirement: Nome ausente e recibos compactos
Quando o nome confirmado do tutor estiver vazio, os rótulos e metadados SHALL explicitar Nome não informado sem preencher dados pessoais por inferência. Os dois checks do recibo Visto SHALL ser desenhados juntos em um único ícone SVG, sem depender do espaçamento entre caracteres Unicode.

#### Scenario: Tutor com nome vazio
- **WHEN** o detalhe autorizado retorna tutor.name vazio
- **THEN** a conversa identifica o perfil Tutor e informa a ausência do nome cadastrado

### Requirement: Dados de contato do tutor no detalhe veterinário
O pop-up do veterinário responsável SHALL apresentar nome, telefone e e-mail cadastrados do tutor proprietário do pet, com fallback Não informado. Contatos SHALL ser projetados somente no detalhe autorizado ao profissional atribuído, sem exposição na fila ou inclusão de CPF, endereço ou credenciais. A consulta SHALL reutilizar o join já existente, sem chamadas adicionais ao abrir o pop-up.

#### Scenario: Veterinário consulta o tutor
- **GIVEN** o profissional é responsável pelo atendimento e o vínculo pet/tutor continua válido
- **WHEN** abre informações
- **THEN** vê os dados de contato confirmados, enquanto terceiros e a fila continuam sem acesso a esses campos

### Requirement: Edição e remoção de mensagens próprias
Durante atendimento humano ativo, cada participante SHALL selecionar mensagem própria enviada e abrir opções Editar/Apagar. O Xano SHALL revalidar participação, autoria, estado e revisão da mensagem dentro da transação. Mensagens do outro participante, contexto do assistente e tickets encerrados SHALL permanecer imutáveis. Edição SHALL preservar horário original e indicar Editada; remoção SHALL substituir o corpo por Mensagem apagada para ambos, sem expor texto removido na resposta. Histórico anterior SHALL ser preservado somente na auditoria privada. Operações SHALL ser idempotentes e alterações concorrentes SHALL ser rejeitadas sem sobrescrever versão nova.

#### Scenario: Editar mensagem própria
- **GIVEN** o participante é autor da mensagem e o atendimento está ativo
- **WHEN** salva texto válido de até 1000 caracteres na revisão atual
- **THEN** ambos veem o novo texto com indicação de edição e a revisão anterior fica na auditoria privada

#### Scenario: Apagar mensagem
- **GIVEN** o participante é autor da mensagem e o atendimento está ativo
- **WHEN** confirma apagar na revisão atual
- **THEN** ambos veem Mensagem apagada e retry da mesma operação não duplica eventos

#### Scenario: Alteração indevida ou concorrente
- **WHEN** alguém tenta modificar mensagem alheia, apagada, encerrada ou com revisão desatualizada
- **THEN** o backend rejeita a mudança sem alterar o conteúdo atual

### Requirement: Prazo para editar e apagar
Editar/apagar SHALL ser permitido somente até 10 minutos contados do horário original de envio no servidor. Mensagens com mais de 600000ms, data inválida ou futura SHALL ser rejeitadas pelo Xano, independentemente de relógio/controles do navegador. Editar SHALL NOT reiniciar o prazo. Retry exato de operação já concluída SHALL permanecer idempotente após o prazo, sem nova alteração. A interface SHALL manter as reticências acessíveis em mensagens próprias ativas e desabilitar Editar/Apagar com aviso quando o prazo expira. O símbolo de mensagem apagada SHALL aparecer depois do texto.

#### Scenario: Vencimento com editor aberto
- **WHEN** a mensagem passa de 10 minutos enquanto o editor está aberto
- **THEN** o rascunho permanece disponível para cópia e salvar/apagar ficam bloqueados, com aviso de prazo

#### Scenario: Limite e retry
- **WHEN** a operação chega até exatamente 10 minutos do envio
- **THEN** pode ser aplicada se as demais regras permitirem, sem renovar o prazo original

### Requirement: Horário de início da conversa
Cada conversa SHALL mostrar um único horário de início centralizado no topo das mensagens, no formato HH:mm. O assistente SHALL usar a abertura local da conversa; atendimento persistido SHALL usar sua criação quando disponível. Atualizações SHALL NOT duplicar o marcador. O símbolo da mensagem apagada SHALL ficar após o texto.

#### Scenario: Abrir e atualizar
- **WHEN** a pessoa abre ou atualiza a conversa
- **THEN** há um único marcador centralizado de início antes da primeira mensagem

### Requirement: Fila geral com responsável exclusivo
A fila SHALL disponibilizar chamados aguardando aos veterinários elegíveis, mas somente um profissional SHALL assumir cada atendimento. A transação e o lock único por ticket SHALL impedir dupla assunção concorrente. Após atribuição, outro veterinário SHALL NOT reassumir ou ler a conversa; o chamado SHALL sair de sua fila geral e continuar acessível somente ao responsável e tutor proprietário.

#### Scenario: Dois veterinários disputam o mesmo chamado
- **WHEN** dois profissionais tentam assumir o mesmo chamado simultaneamente
- **THEN** exatamente um é responsável e o outro não acessa a conversa nem consegue reassumir

### Requirement: Cabeçalho em linhas e ações do tutor
O cabeçalho humano SHALL organizar nome, identificação do perfil, pet e status em linhas separadas. Cartões do tutor SHALL usar Ver conversa em todos os estados, sem alterar permissões ou criar outro chamado ao abrir.

#### Scenario: Abrir a lista do tutor
- **WHEN** o tutor visualiza os cartões
- **THEN** os botões correspondem ao estado e abrem somente o atendimento próprio existente
