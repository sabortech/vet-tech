# Organização da aplicação

Este documento registra a estrutura recomendada para o código Python/Reflex do
VetTech. A organização deve evoluir gradualmente conforme cada funcionalidade
for implementada; não é necessário criar pastas vazias nem mover todo o código
existente de uma vez.

## Estrutura recomendada

```text
vet_tech/
├── vet_tech.py             # ponto de entrada Reflex e registro do app/páginas
├── pages/                  # telas associadas a rotas
├── components/             # componentes de interface reutilizados
├── features/               # estado e lógica agrupados por funcionalidade
│   ├── auth/
│   ├── dashboard/
│   ├── tutors/
│   └── pets/
└── shared/                 # integrações e utilitários compartilhados
    └── xano_client.py

tests/
├── unit/
└── integration/

xano/                       # fonte única e autoritativa dos artefatos XanoScript
docs/                       # documentação durável do projeto
openspec/                   # propostas, especificações, designs e tarefas
```

Os diretórios podem ser introduzidos à medida que forem necessários. A
estrutura acima é uma direção para novos módulos, não exige que a aplicação
atual seja reescrita antes de continuar o desenvolvimento.

## Responsabilidade de cada pasta

- **`pages/`**: funções de página e composição das telas ligadas a rotas do
  Reflex. Nem toda view precisa ter uma rota própria; fluxos como alternar
  entre login e cadastro podem ser partes da mesma página.
- **`components/`**: funções que retornam componentes Reflex reutilizáveis,
  como campos de formulário, cabeçalhos e cartões. Evitar colocar aqui estado
  de negócio, chamadas ao Xano ou páginas inteiras que não sejam reutilizadas.
- **`features/`**: estado Reflex, manipuladores de eventos, validações e
  operações específicas de cada capacidade do produto. Agrupar por domínio
  (`auth`, `tutors`, `pets`) mantém próximas as partes que mudam juntas.
- **`shared/`**: código realmente comum a várias funcionalidades, como o
  cliente HTTP do Xano e configuração compartilhada. Não antecipar abstrações
  antes de haver reutilização concreta.
- **`tests/`**: testes unitários e de integração. Testes que usam serviços
  externos devem ser identificados como integração e não depender de produção.

## Convenções de dependência

- `pages/` compõe componentes e conecta a interface ao estado das
  funcionalidades.
- `components/` não deve importar páginas nem controlar autenticação ou regras
  de domínio.
- `features/` pode usar `shared/` para integração, mas regras de autorização
  devem continuar garantidas pelo backend Xano.
- Segredos e credenciais não devem ser escritos em código, páginas,
  componentes ou documentação; usar configuração por ambiente.
- `shared/dates.py` separa datas civis ISO de instantes Xano em milissegundos
  ou ISO com offset. Datas civis mantêm seu dia; instantes são apresentados no
  fuso America/Sao_Paulo. `components/date_input.py` confirma a data selecionada
  em formato brasileiro e compartilha o painel de calendário com seletores de mês/ano
  e LED SVG entre agenda, atendimento, agendamento do tutor e nascimento do pet.
  O agendamento integra pet, veterinário compatível, dia e horário na primeira etapa e bloqueia dias passados;
  a data escolhida é espelhada em um campo somente leitura junto ao horário,
  sem preencher automaticamente a hora da consulta;
  o nascimento mantém seu rascunho ISO, bloqueia dias futuros e permite limpar
  o campo opcional. Dias reais indisponíveis ficam visíveis e desabilitados,
  enquanto espaços vazios do mês ficam ocultos. Cada fluxo conserva seus eventos e estado;
  os campos do atendimento continuam gravando valores ISO no rascunho existente.
- Manter os artefatos do backend em XanoScript e continuar tratando Xano como
  backend. Esta organização não introduz outro framework ou serviço.

## Aplicação gradual

### Navegação compartilhada do tutor

A marca da sidebar centraliza nome Vet Tech e a tartaruga em V de
`assets/consultation-pdf/mascote-v.png`. Os controles de abrir/recolher usam
três barras em todos os estados, mantendo rótulos e aria-expanded dinâmicos.

O layout padrão do tutor compõe o mesmo menu em todas as telas: entradas
principais seguidas de Mudar pet e Configurações, nessa ordem, com somente Sair no rodapé.
As ações são compostas via import local para evitar ciclo de imports com pets;
O cadastro fica em Meus Pets, sem entrada Novo pet no menu. Mudar pet e Sair usam o guard de
descarte nas Configurações. A navegação pode rolar em telas baixas, mantendo
o rodapé acessível. O menu veterinário mantém sua composição própria.

`components/sidebar.py` contém o catálogo visual único e `layout_com_menu`, usado
por Meus Pets, Configurações, Dashboard e Prontuário. A referência é a sidebar verde existente
com marca, pill ativo branco, ícones e tokens `.sidebar-*` de `assets/vet_tech.css`.
O layout aceita ações por composição; `components/navigation.py` fornece somente
as ações clínicas e o modal, sem criar uma segunda sidebar ou estado de pet.

Ordem das entradas: Dashboard, Prontuário, Vacinas, Medicamentos, Doenças,
Consultas, Exames, Meus Pets e Configurações. Dashboard está habilitado para tutor;
Exames segue sem destino funcional na interface.
O catálogo visual deriva os destinos clínicos da allowlist de
`features/navigation/state.py`, também usada pelo guard do servidor.

`/dashboard` apresenta a visão geral ou individual do tutor a partir de leituras
autenticadas por pet em Xano. “Todos os pets” solicita cada pet próprio com até
quatro chamadas concorrentes em um worker background; a sessão fica livre durante
a espera por HTTP e eventos repetidos do mesmo carregamento são deduplicados.
O lote reutiliza um transporte HTTP de duração limitada, com headers por request,
sem compartilhar credenciais ou cache entre sessões. Os resumos aparecem
progressivamente, mantendo a ordem dos pets; a indicação de carregamento permanece
até terminar o lote. Leituras completas podem ser reaproveitadas por até 15 segundos
na mesma sessão e dia, se a lista de pets não mudou. O botão Atualizar força nova
leitura; logout e ações clínicas/agendamento invalidam esse reaproveitamento.
O escopo individual envia somente o `pet_id`
selecionado. Cada consulta clínica também valida a propriedade no backend e aplica
ordenação e limites específicos para próximas datas, pendências e atividade recente.
A visão geral usa cards completos com foto retangular, identificação, três
indicadores, faixa decorativa de vacinas, acompanhamento detalhado e quatro
ações. A página compõe o `booking_dialog(show_trigger=False)` existente para
que o agendamento dos cards abra o mesmo fluxo clínico sem um botão duplicado.
A faixa indica o prazo registrado da próxima dose por LED e texto, com verde
para mais de sete dias, amarelo de um a sete dias, âmbar hoje, vermelho para
a data ultrapassada mais recente quando não houver futura e apagado sem data
válida. A faixa abre Vacinas do pet e não representa percentual de vacinação.
O contorno SVG do card acompanha a cor da faixa em movimento horário por CSS;
sem data fica apagado e com movimento reduzido continua girando mais devagar, sem
interceptar ações ou gerar eventos remotos.
A referência é calculada no carregamento pelo dia local de São Paulo. A grade usa duas colunas
quando a largura útil permite e uma nas demais telas; cards da mesma linha
compartilham a altura determinada pelo maior conteúdo e alinham as ações na base,
sem cortar os textos. O fundo local
`assets/fundopets.jpeg` cobre a área principal nos dois escopos. Os estilos
`dashboard-*` em `assets/vet_tech.css` limitam a apresentação ao Dashboard.
O filtro do Dashboard é independente de
`selected_pet_id`; somente uma ação explícita de agendamento ou navegação para o
prontuário define o pet de contexto da ação. As projeções derivam idade e mensagens
de acompanhamento dos registros consultados, com peso cadastrado apresentado em Kg, sem inferir saúde
geral ou cuidados completos. Falhas de leitura permanecem distintas do estado vazio.
O endpoint fonte está em `xano/api/clinical/tutor/dashboard_GET.xs`, no grupo
`Clinical`, e precisa estar publicado no ambiente Xano usado pela aplicação.
Ele valida o pet com `Clinical/assert_owner` e repete o filtro de propriedade
nas consultas clínicas; a tela não depende das APIs de histórico sem limite.

Prontuário representa Início. As demais seções usam `/prontuario?secao=<chave>`;
as chaves permitidas são `inicio`, `vacinas`, `medicamentos`, `doencas` e `consultas`.
A entrada de página aplica a intenção inclusive em mudança de query e histórico
do navegador. Sem pet alvo, essas cinco seções apresentam a mesma orientação ilustrada com
botão para Meus Pets (`/`); a lista de escolha fica somente em Meus Pets.
O wallpaper cobre toda a área principal sem moldura, usando `assets/fundpet.jpeg` no claro e a variação
`assets/fundpet-dark.png` no escuro, alternadas pelo tema CSS existente,
com texto e botão reais na área superior livre da imagem.
O fundo usa contain centralizado para preservar a cena inteira, com cor de
fundo completando a largura disponível e alinhamento inferior no celular.
`fundpet-pattern.svg` no escuro e `fundpet-pattern-light.svg` no claro
repetem ossos e patinhas em toda a área principal, com a arte central em
uma camada decorativa e bordas laterais suaves.
Mudar pet e Voltar à lista limpam o contexto e abrem essa lista; Abrir pet
inicia a seleção existente e abre o Dashboard com o filtro no pet escolhido,
reutilizando set_dashboard_scope e preservando loading e erros.
Dashboard global e Configurações não exigem pet.
O estado clínico mantém seleção, cache e carregamento; o menu não
cria uma sessão paralela nem faz HTTP para renderizar ou alternar expansão.

`NavigationState.sidebar_preference` conserva a preferência desktop existente;
`drawer_open` é transitório e independente, abaixo de 768 px. O guard de
Configurações valida o destino exato e só o executa depois do descarte confirmado.
As páginas compõem as dependências para evitar o ciclo sidebar → pets → sidebar.

O arquivo `vet_tech/vet_tech.py` atualmente concentra a entrada do app, estado,
comunicação HTTP, páginas e componentes. Novas funcionalidades podem ser
separadas por domínio sem exigir uma migração total imediata. Ao extrair um
módulo, preservar os fluxos existentes e verificar imports, registro de rotas
e build do Reflex.

Os artefatos XanoScript oficiais ficam somente em `xano/`. Não criar nem manter
cópias de `api/`, `table/`, `function/`, `workspace/`, `addon/` ou `ai/` na raiz.
Se arquivos XanoScript aparecerem na raiz, consolidar suas alterações com a
versão autoritativa em `xano/` antes de remover a cópia; não manter duas árvores
de workspace.

### Assistente n8n

O chat humano continua no domínio `features/support_chat/`; o transporte
autenticado está em `shared/support_client.py`. A ponte global usa as ações
`support_*` e só repassa campos operacionais permitidos. Contexto confirmado,
identidade, token e credencial de criação ficam privados no servidor Reflex.
O Xano verifica propriedade/participação novamente e serializa transições em
`Support/operate`, no grupo `vettech-support`. O agregado `support_ticket`
mantém contexto, mensagens e eventos; `support_lock` protege concorrência.
Não se introduz serviço alternativo, autorização clínica ou consulta automática.
O painel usa os controles existentes e consulta o atendimento ativo a cada vinte
segundos, suspendendo consultas quando fechado, em aba oculta ou encerrado.
A lista só atualiza por ação explícita; encaminhamento consulta apenas pets.
Falhas oferecem retry manual idempotente, sem repetir escritas automaticamente.
Ver `docs/chat-veterinario.md` para contrato, operação e verificação.

`features/support_chat/state.py` fornece o mixin de conversa do State existente;
`shared/n8n_client.py` contém transporte HTTP e validação de contrato. O wrapper
global publica um formulário Reflex oculto, sem credenciais, e os assets mantêm
somente apresentação, animação e histórico visual. Nome, perfil, token e contexto
de envio são derivados pelo servidor. Ver `docs/n8n-chat.md` para configuração e
limites de publicação/validação.

### Configurações compartilhadas por perfil

Cartões de Minha conta, Segurança e Preferências reutilizam perimeter_led
verde com posicionamento relativo e isolamento explícitos em cada cartão.
O contorno decorativo acompanha a borda de 20 px, não intercepta eventos e
reduz a velocidade quando a preferência de movimento reduzido está ativa.

`pages/configuracoes.py` compõe a mesma experiência para tutor e veterinário.
`features/settings/state.py` mantém rascunho, cache e operações com contexto de
token, perfil, identidade e geração da sessão. Contratos de conta/senha são
separados por domínio no grupo Authentication; o médico não chama rotas do tutor.
Seu menu reutiliza a sidebar e oferece Horários, Consultas e Configurações.
A navegação de retorno usa `/?secao=horarios` e `/?secao=consultas`, com intenção
aplicada na entrada da agenda e destinos validados no guard de configurações.
Os campos profissionais permanecem somente leitura; o backend permite apenas
nome/telefone e valida a senha atual antes de alterá-la.

### Identidade profissional na sidebar médica

`veterinary_actions` apresenta avatar de iniciais, rótulo Veterinário(a), nome e
CRMV/UF da própria conta. O estado autenticado mantém somente os metadados
necessários e os carrega em background pelo endpoint `veterinario/account` já
existente, uma vez por sessão confirmada. A leitura de Configurações reutiliza
os valores recebidos para sincronizar o card; o nome continua vindo de
`identity_name`. Falha, ausência e carregamento são explícitos, com nova tentativa
local. Token/perfil/identidade/geração protegem a resposta, e logout limpa os
metadados. Não há consulta de registro externo nem selo de validação profissional.
A apresentação mantém avatar/saída no menu compacto e card completo no drawer.

A orientação sem pet reutiliza `perimeter_led` em uma moldura SVG verde
que acompanha o contorno da cena central nos dois temas. O segmento gira no
sentido horário via CSS, mais lentamente com movimento reduzido, sem eventos
remotos ou interceptação de cliques.

Mudar pet usa `/?selecionar=pet` para mostrar somente `pet_list` com a mesma
tartaruga `/optimized/espreitando.webp` do calendário à esquerda. A query atual
define o modo, permitindo histórico do navegador e retorno a `/` com cadastro
e lista completos. O seletor reutiliza loading, vazio, atualização e ação de
abertura existentes; não cria outra sessão nem outra consulta de pets.

Os dois cartões de Meus Pets, cadastro e lista, reutilizam perimeter_led
verde horário no contorno, sem interceptar cliques, com ciclo reduzido de
20 segundos para preferência de movimento reduzido.

A lista de Meus Pets usa grade com coluna uniforme para ações. Seleção
autorizada aparece no próprio botão, com check, texto “Pet selecionado”,
cor sólida e aria-pressed. A leitura de detalhes usa “Carregando…” no botão;
metadados longos quebram sem deslocar a coluna e telas estreitas reposicionam
a ação abaixo dos detalhes.

O Prontuário selecionado compõe um hero com foto circular de borda neutra
fina, nome, espécie/raça e mascote existente, seguido por cinco cartões de
sexo, nascimento, peso, pelagem e microchip. A projeção autorizada acrescenta
foto validada e nascimento legível mantendo a data bruta e valores zero.
Peso cadastrado usa Kg, conforme a convenção do atendimento; valores ausentes ficam como “Não informado”, sem unidade solta. CSS pet-record-*
limita a apresentação ao Prontuário, com tema escuro e composição móvel;
loading, erro, voltar, agendar e atualizar usam os fluxos existentes.

O endpoint de detalhes de pet inclui `foto`; enquanto ambientes publicados
ainda omitirem a chave, o Prontuário reutiliza a URL validada da lista própria
somente para o mesmo ID já autorizado. Foto explícita no detalhe, inclusive
nula, prevalece sobre a lista para respeitar atualização ou remoção.

O hero, a moldura circular da foto e os cinco cartões do Prontuário
reutilizam perimeter_led verde horário nos dois temas, decorativo e sem
interceptar ações. As curvas seguem cada moldura; movimento reduzido usa
ciclo de 20 segundos.

A faixa central do hero usa `fundopets.jpeg` com recorte CSS cover alinhado
ao topo, preservando a textura original. No escuro recebe overlay verde
profundo como o Dashboard. A camada é decorativa e não intercepta ações.

A aba Vacinas conserva cabeçalho e lista simples, com apresentação própria
`vaccine_record_card`: identificação, grade de aplicação/lote/próxima dose
e rodapé com origem, veterinário e botão compacto. CSS vaccine-record-* usa
tokens dos temas e empilha dados no celular; registros nas demais seções
e dentro de consultas mantêm sua apresentação anterior.

O cabeçalho de Vacinas organiza título/descrição e um grupo com contexto do
pet (foto/nome) e Atualizar, em uma linha no desktop e duas no celular,
preservando o evento clínico e seus bloqueios durante carregamento.

O cartão da aba Vacinas usa duas colunas: dados à esquerda e imagem
decorativa `fundo.jpeg` à direita. Aplicação, veterinário, lote e consulta
ficam em grade, seguidos da próxima dose registrada e ação de origem. No
celular a imagem fica abaixo; o escuro usa overlay suave. Não se inferem
status de vacinação completa nem próximas doses além das cadastradas.

O cartão dividido de vacina reutiliza perimeter_led verde no contorno
externo completo (dados e imagem), com órbita horária, sem interceptar
ações. Os cantos externos da imagem acompanham o raio do cartão e o halo
fica livre de recorte; movimento reduzido usa ciclo mais lento.

O painel ilustrado de Vacinas centraliza um ícone de seringa em disco
decorativo sobre o cenário, com contraste próprio nos dois temas e tamanho
reduzido no celular. A ilustração não intercepta cliques nem altera dados.
Medicamentos reutiliza esse disco com ícone de cápsula, substituindo a
tartaruga apenas nessa aba. Ambos os discos usam fundo com 70% de opacidade;
o painel de Doenças usa o mesmo disco com ícone de coração com pulso.

Medicamentos usa `medication_record_card` somente na listagem da aba:
cartão dividido padronizado com Vacinas, com grupos de dose/frequência/via/tipo,
datas e proveniência, além da ação de consulta e LED horário no contorno. O cabeçalho alinhado é compartilhado por composição
com Vacinas. O painel interno direito recebe um ícone decorativo de cápsula
em disco translúcido, abaixo dos dados em telas menores. O recorte
`tutu-sem-fundo.png` de `tutu.jpeg` permanece preservado nos assets. Não se
infere status Ativo, pois o contrato de medicamento não contém esse campo.

Os painéis laterais de Vacinas, Medicamentos, Doenças, diagnósticos pontuais,
Exames e Consultas recebem `fundo_card`,
sorteado entre fundo.jpeg, fundo02.jpeg, fundo_mar.jpeg e fundinho.jpeg somente após
validar o contexto da resposta clínica. Um mapa privado por sessão/pet/tipo/
registro mantém escolhas estáveis e prioriza variedade até esgotar catálogo.
Logout limpa o mapa; nenhuma gravação clínica ou consulta remota adicional
é feita. Em Medicamentos a cápsula permanece fixa e só o fundo varia.

Na visão Todos os pets do Dashboard, o card do pet clínico selecionado em
Meus Pets apresenta um indicador no cabeçalho, entre seu nome e a mascote
em V. O clique abre seu escopo individual via set_dashboard_scope. Sem
seleção e nos demais cards o indicador não aparece. A composição é interna
ao cartão e adapta o texto ao celular, sem controle flutuante adicional.


Doenças usa `disease_record_card` exclusivamente na listagem, com o mesmo
cabeçalho de Vacinas e Medicamentos, cartão dividido, ícone de coração com pulso em disco translúcido, cenário otimizado
e LED verde. O estado clínico aparece uma vez, legível, seguido de evolução,
consulta, veterinário e descrição com quebras de linha preservadas. Ausências
permanecem explícitas; notas recentes não são simuladas. A ação de origem usa
o detalhe autorizado existente; complementos dentro das consultas usam a variante
compacta própria do documento clínico descrita abaixo.
Classes disease-* limitam ajustes de apresentação aos novos cartões.

### Eficiência de carregamento e entrega

O Dashboard individual usa `dashboard-individual-card` como superfície única
para identificação, indicadores, cuidados, atividade e ações de qualquer pet.
As informações são agrupadas por seções internas; o LED externo reutiliza a
cor da próxima dose, assim como a sombra do cartão individual. Sem data,
o LED fica apagado e a sombra neutra, conforme a barra, sem indicar estado
clínico positivo por decoração. A visão geral mantém sua sombra anterior.
Não modifica o filtro, as consultas Xano nem os handlers das ações.

O fundo principal das abas no tema claro usa `--vt-page-bg: #efede6`,
incluindo Dashboard e áreas clínicas, substituindo fundos de página anteriores.
As imagens dentro dos cartões e as cores próprias do modo escuro permanecem.
A orientação sem pet é exceção: conserva o fundo estampado claro anterior
com `fundpet-pattern-light.svg`, além da cena ilustrada e LED existentes.
Meus Pets, Mudar pet e Configurações compartilham essa estampa, incluindo a versão escura
`fundpet-pattern.svg`, sem mudar o layout dos cartões ou a tartaruga lateral.
A estampa também cobre `.app-layout` por trás da sidebar, evitando cantos
de outra cor nas bordas arredondadas do menu.
O Dashboard compartilha o raio direito de 24 px do menu das demais telas.
No tema claro seu fundo externo usa o mesmo bege; no escuro layout e página
compartilham as camadas de fundo fixadas ao viewport para alinhar os cantos.

A sombra dos cartões fora do Dashboard usa `--vt-card-green-shadow`,
com contorno e halo verde suaves. Seletores de superfícies de cartões excluem
explicitamente os descendentes de `.dashboard-page`, preservando as sombras
e cores de status próprias do Dashboard. Campos e botões não recebem o halo.

Consultas do tutor compartilha o cabeçalho clínico e usa `consultation_card`
na lista, com LED e calendário em disco translúcido. O detalhe organiza
metadados e narrativas em um cartão único com painel ilustrado à direita,
reutilizando o fundo sorteado da consulta e prancheta em disco translúcido.
Os complementos ficam separados por categoria, mantendo
diagnóstico pontual separado das condições consolidadas. Vacinas, Medicamentos
e Doenças reutilizam os cartões completos das abas com show_origin=False.
Doenças usa modo de diagnóstico com data/observações próprias da consulta.
Exames usa `exam_record_card`, com o mesmo shell dividido, LED e símbolo de
tubos em disco translúcido. Solicitação, realização, resultado, profissional
e data legada disponível continuam apresentados. Nenhum cartão do detalhe
oferece botão de origem redundante. As imagens usam as versões WebP locais.
Títulos ficam acima dos valores e descrições preservam quebras de linha.
Permissões/auditoria ficam em superfície separada e continuam sob demanda.
Esse bloco usa o mesmo cartão dividido, com escudo em disco translúcido e
imagem lateral; controles de autorização e auditoria permanecem no corpo.
CSS consultation-* limita o layout; exportação e handlers existentes não mudam.
O cabeçalho de Consultas agrupa pet, Voltar, Atualizar e PDF elegível junto ao
título, eliminando a toolbar separada. Feedback de exportação só ocupa espaço
quando há mensagem. Em telas estreitas as ações se reorganizam em grade.

A seleção autorizada de detalhes do pet agenda o histórico clínico somente
quando a rota atual é `/prontuario`. No Dashboard, resumo e identificação
continuam disponíveis sem as duas consultas antecipadas de histórico/agenda.
A primeira entrada clínica, inclusive enquanto detalhes estão carregando,
usa o guard/worker existente, com deduplicação e validação de geração.

Listagem/raças, detalhes/raças e lote clínico usam `xano_request_batch` para
reutilizar conexão dentro da operação. Contextos aninhados reutilizam o
cliente externo e não o encerram antes do fim da operação. Headers de sessão
continuam por request; nenhum transporte ou cache de dados é compartilhado
permanentemente entre usuários. Catálogos de raças usam até quatro leituras
concorrentes, preservando resultados parciais e invalidação por sessão.

`assets/optimized/` contém versões WebP de cenários e mascotes e favicon PNG
compacto, gerados por `scripts/optimize_ui_assets.py`. Os originais são
preservados, inclusive para edição futura; fotos remotas dos pets não mudam.
O app serve os assets gerados diretamente, sem conversão em runtime. O
manifesto registra dimensões e bytes. A política de retries e os TTLs
clínicos não foram alterados por esta otimização.

### Prévia e exportação de consultas

`components/consultation_pdf.py` concentra o diálogo comum aos perfis tutor e veterinário, com um único exemplar por página relevante. Os acionadores do cabeçalho tutor, confirmação do atendimento e cartões profissionais usam o mesmo estado clínico e DTO. O estado serializado guarda título, estados de carregamento e token de instância; bytes de PDF, assinatura do DTO e operação permanecem privados. Um evento efêmero entrega os bytes ao PDF.js local, sem URL pública ou armazenamento no navegador. Fechar/desmontar invalida a geração e limpa os campos da prévia. ReportLab gera a prévia em thread com os limites existentes; a confirmação revalida acesso e conteúdo e reutiliza os bytes privados quando iguais. O visualizador renderiza páginas progressivamente e destrói o documento ao fechar.

GET de prévia e POST de exportação são operações distintas e auditadas; a função `Clinical/consultation_document` em `xano/function/clinical/` monta somente o recorte da consulta publicada após autorização do chamador. O médico permanece na confirmação após finalizar para poder baixar, sem redirecionar e recarregar a agenda; o catálogo de edição não é carregado para atendimentos finalizados. Deduplicação limita a uma leitura por painel aberto e uma exportação pendente, sem cache global de dados clínicos.

O agendamento do tutor apresenta pet e veterinário no painel inicial do calendário. Trocar o pet limpa o profissional e atualiza os médicos compatíveis; respostas antigas são descartadas. A segunda etapa resume os nomes e solicita motivo e confirmação com aviso de acesso prévio. O vínculo é por consulta, permitindo pets com médicos diferentes e novos médicos em consultas futuras, conforme autorização do tutor.

A orientação clínica sem pet inclui o convite “Gostaria de agendar uma consulta?” abaixo da seleção existente. O diálogo local em `components/pets.py` reutiliza a tartaruga e oferece dois cards: Mudar pet pelo handler existente ou cadastro em Meus Pets (`/`). Não cria sessão, consulta ou nova leitura; os cards ficam em duas colunas e se empilham em telas estreitas.

O painel de orientação mantém a tartaruga na borda externa junto ao LED, conteúdo rolável internamente e cards HTML retangulares de raio 18px, excluídos do arredondamento global de botões. O realce dos controles habilitados usa `--interaction-light`, priorizando cor explícita da ação, status clínico, consulta, prazo de vacina e verde padrão. Hover e foco usam halo por drop-shadow para preservar sombras existentes; controles desabilitados e somente leitura não recebem o halo.

### Conversas privadas entre veterinário e tutor

O domínio existente `features/support_chat` recebe eventos `direct_*` em sua ponte privada e usa `shared/direct_client.py` para os endpoints autenticados de conversas. `xano/function/direct/operate.xs` e `direct_conversation` mantêm pares privados independentes de `support_ticket`; nenhum identificador de pet ou contexto do assistente é compartilhado. O JavaScript adapta o DTO direto ao apresentador/compositor comum com `kind=direct`, roteando operações para a API correta e ocultando controles clínicos. O diretório de tutores é exclusivo do veterinário; o diretório de veterinários é exclusivo do tutor. Ambos retornam somente nome/ID em páginas de 20 e permitem iniciar o mesmo par privado em qualquer direção. Dados e credenciais não ficam em armazenamento persistente do navegador.
