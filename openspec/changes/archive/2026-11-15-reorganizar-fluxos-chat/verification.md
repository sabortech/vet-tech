# Verificação

- 26 testes unitários do estado e cliente n8n: OK.
- `reflex compile --dry`: OK.
- `node --check assets/support-chat.js`: OK.
- `openspec validate reorganizar-fluxos-chat --strict`: OK.
- Playwright com assets reais e ponte simulada: OK em 390px escuro, 1366px claro, 320px claro e 390px claro.
- Cenários: encaminhamento sem listar tickets; retry de criação preservando campos e chave; polling ativo a 20s; nenhuma leitura periódica na lista, aba oculta, encerrado e painel fechado; conversa nova limpa. Evidências PNG em evidence/.
- Nenhuma chamada real ao Xano ou n8n; disponibilidade remota e produção não verificadas. Mudanças permanecem locais e exigem publicação/reinício do backend Reflex no ambiente de destino.

## Banner no servidor local

A verificação posterior identificou cópias antigas em `.web/public/support-chat.css`
e `.web/styles/support-chat.css`; `compile --dry` não atualizou essas cópias.
Ambas foram sincronizadas com o asset fonte. Navegador contra a aplicação real
em `localhost:3000/login` confirmou vídeo de 378 × 213px, largura integral e
`max-height: none`, sem envio de mensagens. Evidência: `evidence/banner-live-restaurado.png`.

## Navegação integrada ao cabeçalho

Conferida na aplicação real em 390px/escuro e 1366px/claro: fundo idêntico
entre identificação e navegação, sem divisória e sem overflow. Cópias geradas
de CSS sincronizadas. Evidências: `evidence/header-integrado-*.png`.

## Correção da configuração de encaminhamento

A credencial de criação estava ausente do .env local. O valor existente foi
recuperado dos metadados do mesmo workspace Xano configurado no aplicativo,
sem publicação ou alteração remota, e gravado somente no .env ignorado.
O backend em desenvolvimento recarregou automaticamente (novo worker confirmado).
31 testes unitários passaram, incluindo ausência de chamada Xano e erro de
configuração não recuperável por retry quando faltar a credencial. Compilação
Reflex, validação OpenSpec e sintaxe JavaScript passaram. Nenhum chamado real
foi criado para verificar a correção; o usuário precisa confirmar novamente
o encaminhamento no chat para validar o fluxo autenticado completo.

## Cores da fila veterinária

Navegador com três cartões simulados confirmou vermelho/aguardando,
amarelo/em atendimento e verde/encerrado nos temas claro e escuro. Borda,
rótulo e botão usam a paleta contextual, sem polling adicional ou LED por cartão.
Assets servidos sincronizados. Capturas em `evidence/vet-status-*.png`.

## Ícone flutuante e detalhes do ticket

Playwright com assets reais e ponte simulada passou em quatro combinações
de tamanho/tema. Verificou abertura sem request extra, fechamento por Escape
sem fechar o chat, retorno do foco, preservação do motivo, cancelamento no
pop-up e suspensão de polling enquanto o pop-up está aberto. Detalhes são
limpos ao sair do fluxo/trocar sessão. Sintaxe JavaScript e OpenSpec válidos.
Assets em .web/public e .web/styles sincronizados. Evidências: ticket-info-*.png.

## Paleta do tutor

As mesmas regras de status agora abrangem tutor e veterinário. Verificação
no navegador com três tickets simulados confirmou vermelho, amarelo e verde
na lista do tutor nos temas claro e escuro. Assets servidos sincronizados;
evidências em `evidence/tutor-status-*.png`.

Halo do ícone flutuante: hover e foco por teclado conferidos no Chromium,
vermelhos no estado aguardando. A variável contextual agora alimenta o efeito
global de interação; cópias de CSS servidas sincronizadas.

## Fotos dos pets

- Projeções de lista/detalhe testadas com fotos deduplicadas, isolamento de
  contexto clínico na fila e foto ausente.
- Playwright: foto válida, ausente e inválida, moldura circular, lista e pop-up
  nos temas claro/escuro e perfis tutor/veterinário, sem busca extra por pet.
- 31 testes Python existentes, sintaxe JavaScript e validação OpenSpec: OK.
- Função Support/operate (359369, workspace 167758) publicada seletivamente,
  com backup privado ignorado. Conferidos ausência de rascunho divergente e
  acordo da lógica anterior antes da alteração. Execução remota read-only com
  ator inexistente confirmou tickets=[] e pet_photos={}, sem acessar usuários
  ou criar registros.
- A primeira publicação foi revertida automaticamente porque a verificação
  não tratava o envelope aninhado do runner. Confirmado sucesso no retorno
  privado, a verificação foi corrigida e a mesma alteração republicada com êxito.
- Assets servidos sincronizados. Fotos reais de usuários não foram copiadas
  para evidências; screenshots usam imagem local de teste.

## LEDs de status nos cartões e fotos

Navegador confirmou um SVG decorativo por cartão e por foto, inclusive com
fallback e no pop-up. Animação de 6s e ciclo reduzido de 12s conferidos por
estilo computado; ações continuam clicáveis e sem consultas adicionais.
Validação OpenSpec e sintaxe JavaScript passaram; assets servidos sincronizados.

## Recorte da foto e identidade humana

A imagem usa camada absoluta recortada em círculo, independente do LED.
Playwright confirmou clip-path e ícones próprios para tutor/veterinário nas
mensagens recebidas e enviadas, cabeçalho com interlocutor/status nos dois
perfis e restauração da mascote ao iniciar nova conversa. Regressão dos fluxos
passou em quatro combinações de tamanho/tema, sem serviços externos. Sintaxe
JavaScript e OpenSpec válidos. Assets servidos sincronizados; evidências
em `evidence/participant-*.png`.

## LEDs da janela e do pop-up

Navegador confirmou stroke vermelho enquanto aguardando e amarelo após
assunção, tanto na janela quanto no novo SVG externo do pop-up. Ao voltar
ao assistente, o status contextual é removido e o LED padrão restaurado.
Halo deriva da mesma cor do traço. Sintaxe JavaScript, OpenSpec e testes
de fotos/identidade passaram. Assets servidos sincronizados.

## Paleta completa por status

Playwright confirmou cabeçalho vermelho aguardando e cabeçalho/envio amarelos
em atendimento, com texto escuro, nos temas claro/escuro. Ícones, campo, foco
e balões usam variáveis contextuais restritas ao ticket. Retorno ao assistente
remove status e restaura a paleta padrão. OpenSpec válido e assets sincronizados.

## Emojis locais

Painel de emojis validado para visitante, tutor e veterinário em celular e
desktop, claro/escuro, incluindo busca sem acentos, categorias, inserção no
cursor/substituição da seleção, limite de 1000 caracteres, Escape, clique
externo, retorno do foco e bloqueio enquanto aguardando. Envio humano
simulado preservou o emoji; seleção não gerou requests. Regressão dos fluxos
passou em quatro combinações, assim como sintaxe JS e OpenSpec.
Assets servidos sincronizados; evidências em `evidence/emojis-*.png`.

## Nomes dos participantes

Rótulos Tutor/Veterinário com nome confirmado aparecem acima de avatar/balão;
o corpo mantém somente a mensagem. O detalhe autorizado projeta tutor.name
por join na consulta do pet existente, sem consulta por mensagem ou exposição
na fila. Cabeçalho usa o nome confirmado do interlocutor e fallback por perfil.
Teste de projeção e Playwright com nomes simulados, inclusive texto contendo
ângulos, passaram nos dois perfis. Publicada seletivamente a função de nomes
com backup privado; execução remota read-only com ator inexistente confirmou
lista vazia e contrato preservado. Assets servidos sincronizados.

A publicação dos nomes usou .venv/support-names-publish.xs para excluir a
restrição de encerramento que ainda aguarda decisão de escopo do tutor.
As tarefas 19 permanecem abertas: código local e testes de restrição foram
preparados, mas a regra final ainda precisa ser reconciliada com a solicitação
posterior de finalização pelo tutor. Não publicar esse trecho sem resolver.

## Entregue/Lido e tutor nos cartões

- 34 testes Python e testes JavaScript de projeção, leitura e autorização
  passaram; compilação Reflex e OpenSpec válidos.
- Leitura testa referência recebida, mensagem própria/inexistente, prefixo de
  mensagens recebidas, preservação de horário, ausência de eventos duplicados
  e proteção do nome do tutor na fila não atribuída.
- Playwright nos dois perfis confirmou nome no cartão, Entregue→Lido, ausência
  de confirmação de mensagem fora da viewport, aba oculta, consumo agrupado
  no polling e descarte de marcadores já confirmados. Regressão geral do chat
  passou em quatro combinações de tamanho/tema.
- Publicada seletivamente Support/operate a partir do baseline remoto de nomes
  e do arquivo privado support-receipts-publish.xs, excluindo a regra de
  finalização ainda pendente. Backup privado preservado; execução remota com
  ator inexistente validou lista vazia e contrato sem ler chamados reais.
- Nenhuma conversa real foi usada para gerar recibos; evidências simuladas
  em evidence/read-receipts-*.png. Assets servidos sincronizados e backend
  local recarregou alterações do mixin pelo modo desenvolvimento existente.

## Correção Entregue → Visto ao trocar de perfil

A confirmação observada ficava aguardando o polling e o foco do destinatário;
a troca rápida de aba podia adiar indefinidamente o envio desse marcador.
Agora há lote após 350ms e envio da leitura já observada ao perder foco, com
intervalo mínimo de 5s entre lotes adicionais. Retornar ao chat consulta
recibos com uma reconferência limitada para cobrir a confirmação em trânsito.
O texto exibido passou para Visto.

Regressão com duas páginas/perfis e backend simulado compartilhado passou:
leitura e retorno antes de 20s mudam Entregue para Visto com uma única
confirmação agrupada. Eventos de foco/visibilidade são explicitamente
simulados porque o Chromium headless reporta ambas as páginas focadas.
Também passou a regressão de viewport/aba oculta/consumo agrupado nos dois
perfis. Nenhuma conversa real alterada. JavaScript/OpenSpec válidos e
asset servido sincronizado. Evidência: read-seen-fast-tab-switch.png.

## Nome ausente do tutor e checks compactos

Diagnóstico read-only do atendimento reportado confirmou que tutor.nome
existe mas está vazio, e que a resposta autorizada retorna o mesmo valor.
Foram impressos somente status e booleanos, sem nome, mensagem ou credencial;
nenhum dado cadastral ou chamado foi alterado. UI passa a explicitar Nome não
informado quando o backend confirma cadastro vazio.

Checks agora usam um único SVG de 16px, sem espaçamento de glifos Unicode.
Playwright confirmou fallback do nome, dois perfis, um único ícone compacto
e atualização Entregue→Visto ao trocar rapidamente de aba. OpenSpec e
JavaScript válidos; assets servidos sincronizados.

## Dados do tutor no pop-up veterinário

Projeção testada para devolver nome/telefone/e-mail somente ao perfil
veterinário após os guards de participação/propriedade existentes. Resposta
do tutor mantém apenas nome e a fila não ganha campos de contato. CPF,
endereço e credenciais não são incluídos. Playwright confirmou a seção
Tutor responsável, contatos simulados e fallback Não informado, sem
consulta ao abrir o pop-up. Publicada seletivamente a função de detalhe
com backup privado, excluindo a regra de finalização pendente. Verificação
remota read-only validou contrato vazio sem ler contatos reais. OpenSpec
e sintaxe JS válidos; assets servidos sincronizados.

## Seleção, edição e remoção de mensagens

- 36 testes Python passaram, incluindo validação dos novos campos, descarte
  de autoria forjada e conflito sem retry indevido. Testes JS de transição
  cobrem autoria, estado, revisão concorrente, idempotência, auditoria privada,
  soft delete e recibo de versão editada; demais testes de projeção/leitura
  passaram. Compilação Reflex: OK.
- Playwright nos dois perfis verificou seleção e menu por clique/teclado,
  edição com texto seguro/emoji, preservação do rascunho após falha, retry
  com mesmo operation_id, Editada, confirmação/cancelamento de exclusão e
  placeholder Mensagem apagada. Mensagens alheias não mostram ações.
- A regressão de dois perfis compartilhando estado confirmou recibos após
  mudanças nas mensagens. OpenSpec e sintaxe JS válidos.
- Support/operate publicada seletivamente com backup privado e verificação
  remota de contrato vazio, sem editar/apagar mensagens reais. A regra de
  finalização pendente continua excluída do arquivo de publicação.
- Assets servidos sincronizados. Evidências simuladas em
  evidence/message-edited-*.png e evidence/message-delete-*.png.

Atalhos de lápis e lixeira conferidos nos dois perfis: lápis abre o editor
diretamente, lixeira abre confirmação; seleção do balão mantém o menu.
Reticências substituídas por SVGs explícitos. Asset servido sincronizado.

## Prazo, símbolo após texto e horário inicial

- Node testa edição/exclusão no limite exato de 600000ms, rejeição após
  limite, data inválida/futura, prazo original imutável e retry idempotente
  após expiração. 36 testes Python e compilação Reflex passaram.
- Playwright verificou expiração no editor aberto sem perder rascunho,
  bloqueio de salvar/opções, resistência ao salto do relógio local, um único
  HH:mm no início, edição/exclusão válidas e símbolo após o texto apagado.
- Janela de 10 minutos publicada seletivamente em Support/operate com
  backup privado e verificação remota vazia; não alterou mensagens reais.
  Assets servidos sincronizados.

## Assunção exclusiva por vários veterinários

Teste real com fixtures sintéticas de desenvolvimento existentes passou:
logins de identidades sintéticas conferidos, um único chamado de teste
criado, duas tentativas sincronizadas por barreira e exatamente um sucesso.
O perdedor foi bloqueado ao reassumir e ler; a lista dele não continha o
chamado atribuído. O chamado sintético foi encerrado no finally e preservado
no ledger privado com seus eventos. Nenhum chamado real foi alterado.
Teste unitário adicional confirma que atendimento atribuído ou encerrado não
aceita nova assunção. Mecanismo existente de lock/transação preservado, sem
alteração de tecnologia ou afrouxamento da participação.

## Cabeçalho, rótulos do tutor e reticências

Cabeçalho humano organizado em três linhas abaixo do nome. Playwright
conferiu separação vertical das linhas nos dois perfis e rótulos Iniciar,
Retomar e Consultar atendimento nos três estados da lista do tutor.

Diagnóstico read-only dos horários no atendimento reportado confirmou que
as mensagens não apagadas verificadas já ultrapassavam 10 minutos; nenhum
conteúdo de mensagem ou nome foi impresso. Reticências agora permanecem
visíveis nas mensagens próprias ativas, e o pop-up apresenta aviso com
Editar/Apagar bloqueados ao vencer, sem relaxar a validação do Xano.
Playwright confirmou expiração com rascunho preservado e reabertura do menu
vencido. Assets servidos sincronizados; nenhuma mudança remota necessária.
