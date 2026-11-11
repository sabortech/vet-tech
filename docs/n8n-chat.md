# Assistente Vet Tech: Reflex e n8n

O chat existente envia perguntas pelo WebSocket Reflex, nunca diretamente ao
n8n. O formulário global oculto publica eventos `State.support_chat` em background.
`features/support_chat/state.py` lê identidade e token privados do State, mantém o
contexto da conversa corrente e chama `shared/n8n_client.py`. A resposta validada
volta por `vettech:chat-response`; o painel renderiza texto seguro.

## Configuração

No `.env` (ignorado pelo Git):

```dotenv
N8N_CHAT_WEBHOOK_URL=https://vet-tech.app.n8n.cloud/webhook/vettech-assistente
N8N_CHAT_WEBHOOK_SECRET=
```

Preencher o segredo com o valor da credencial Header Auth do n8n, cujo nome de
cabeçalho deve ser `X-VetTech-Secret`. Não colar o segredo em código, conversa,
URL, capturas ou ferramentas de frontend. O processo precisa reiniciar após
alterar `.env`; as variáveis são carregadas no launcher ou no ambiente do servidor.
O login do app continua funcionando se a configuração do chat estiver ausente;
nesse caso o chat retorna erro genérico, sem respostas locais simulando IA.

Use a URL de produção `/webhook/` para o aplicativo. A URL `/webhook-test/`
depende do registro temporário de teste no editor do n8n e não substitui o
endpoint de produção. Em 11/11/2026, o endpoint de teste configurado localmente
retornou HTTP 404 (webhook não registrado), enquanto o equivalente de produção
respondeu com contrato válido usando o mesmo segredo. A configuração local foi
corrigida pelo usuário. Após alterar `.env`, carregue o ambiente novamente no
processo do aplicativo; o teste direto não atualiza um servidor já iniciado.

## Contrato

POST HTTPS configurado, `Content-Type: application/json`, `X-VetTech-Secret` e,
somente para pessoa autenticada, `X-VetTech-User-Token`. Sem redirects, retries
automáticos ou logs de payloads/credenciais. Timeout total: 60 segundos; a UI tem
limite de 65 segundos incluindo transporte Reflex e oferece tentativa manual.

Corpo: `request_id`, `conversation_id`, `message`, `user` e `history`. IDs são
UUIDs. Mensagem contém 1–1000 caracteres. `user` é derivado da sessão do servidor:
visitante usa `{authenticated:false,name:null,role:"visitante"}`; pessoa autenticada
usa nome/perfil confirmados e token apenas no cabeçalho. Campos de identidade ou
histórico enviados pelo navegador não são usados para autenticação/contexto.
O n8n confirma a identidade no Xano e as APIs Xano preservam autorização/auditoria.

`history` contém apenas pares de perguntas/respostas bem-sucedidos anteriores da
conversa corrente, até 20 itens/20 mil caracteres. Não inclui saudação local,
erros, indicador de digitação, mensagem atual nem histórico visual arquivado.
Retry não duplica a mensagem no painel e recebe novo request_id. O cliente não
implementa idempotência remota: uma tentativa manual pode executar o workflow
novamente. Nenhuma escrita clínica nova foi introduzida.

Resposta: `ok`, `request_id`, `conversation_id`, `reply`, `error`. Os IDs devem
coincidir. Sucesso exige HTTP 200, ok true, reply textual não vazio e error null.
Erros estruturados reconhecidos: INVALID_REQUEST/400, SESSION_INVALID/401,
XANO_UNAVAILABLE/503 e AI_UNAVAILABLE/503. SESSION_INVALID com ok false também é
reconhecido se o workflow usar HTTP 200 por engano. Erro de credencial do webhook
(401/403 sem o contrato válido) não desloga a pessoa: é falha de configuração.
Erros técnicos/JSON inválido/timeout mostram mensagem genérica. SESSION_INVALID
válido expira a sessão local e o app solicita novo login.

## Validação operacional em 31/10/2026

Após recompilar e reiniciar a instância de produção local com
`bash scripts/run-local.sh`, o smoke real em `http://localhost:3001` confirmou
o ciclo navegador → Reflex → n8n → navegador com resposta de sucesso do workflow.
O usuário também confirmou o funcionamento. A instância anterior servia uma
versão sem o controlador do chat; alterações em produção exigem recompilação e
reinício. O segredo permanece somente no `.env` local, ignorado pelo Git.

Essa verificação usou uma pergunta genérica de visitante. Não comprova consultas
clínicas autenticadas ou o tratamento remoto de expiração de sessão abaixo.

## Publicação do workflow

### Verificação operacional em 11/11/2026

Após a correção da URL local pelo usuário para produção, o smoke
`scripts/n8n_chat_smoke.py` confirmou sucesso pelo cliente real (7,8 segundos).
Os 15 testes de `test_n8n_client` e `test_support_chat_state` passaram. A ferramenta
também foi verificada com configuração inválida: retornou `CONFIGURATION_ERROR`,
metadados seguros e código de saída 1.

A instância de produção já disponível em `http://localhost:3000`, com página de
login acessível, passou no `n8n_bridge_smoke.py` usando Chrome headless:
navegador → Reflex → cliente n8n → navegador, com sucesso verdadeiro do workflow.
Não foi necessário reiniciar a instância. O smoke aguarda a hidratação da ponte
e a animação de abertura do painel; resposta de erro do workflow falha o teste.

```powershell
.venv/Scripts/python.exe -m unittest tests.unit.test_n8n_client tests.unit.test_support_chat_state -q
.venv/Scripts/python.exe tests/integration/n8n_bridge_smoke.py --url http://localhost:3000 --chromium "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

As chamadas reais usaram somente pergunta genérica de visitante. Não validam
consultas clínicas autenticadas nem tratamento remoto de expiração de sessão.
Não houve alteração no código da aplicação ou implementação do chat entre tutor
e veterinário. O `.env` permaneceu ignorado pelo Git e nenhuma credencial foi
incluída nas evidências. Para repetir, adapte a porta e o executável do navegador
ao ambiente em uso.

Na implementação inicial, havia relato de versão antiga em produção que
ignorava o token e de versão nova em rascunho. Antes de validar consultas
clínicas, confirmar que a versão publicada verifica o token e respeita permissões.

Corrigir no workflow o erro conhecido: se uma consulta Xano retornar 401 após a
confirmação inicial da identidade, devolver HTTP 401, ok false e
`error.code = "SESSION_INVALID"`. Se retornar ok true e apenas escrever um pedido
de login em reply, o Reflex não pode distinguir esse texto de uma resposta normal
com segurança. Não interpretar texto da IA como estado de autorização.
A publicação/correção do fluxo remoto não é feita por esta implementação.

## Conversas e privacidade

Abrir gera nova conversation_id; fechar/minimizar invalida a requisição pendente.
O histórico visual mantém somente as últimas 20 conversas nesta aba; login/logout,
troca de identidade ou recarga apagam esse histórico. O backend guarda somente o
contexto corrente em campos privados. O botão de histórico não chama o n8n.
Respostas antigas não são exibidas se conversa, sessão, token ou requisição mudarem.
O controle inicial impede submissão nativa/navegação antes da hidratação: envios
aguardam `vettech:chat-ready`, publicado após montagem pelo Reflex.

No n8n, revisar retenção de execuções para não armazenar tokens nem conteúdo
clínico desnecessário. O modelo deve receber só os campos necessários; o segredo
e o token não devem entrar no contexto da IA.

## Verificação

Teste real e independente do servidor local, com pergunta genérica de visitante
(pode executar o workflow e consumir IA):

```powershell
.venv/Scripts/python.exe scripts/n8n_chat_smoke.py
```

Em ambientes Unix, use `.venv/bin/python`. A ferramenta carrega o `.env` da raiz,
respeitando variáveis já definidas no processo, reutiliza o cliente real e imprime
somente sucesso, código de erro seguro e duração. Código de saída zero exige
resposta válida do workflow; falhas retornam código diferente de zero. Não imprime
URL privada, mensagem, resposta, IDs, tokens ou segredo.

```bash
.venv/bin/python -m unittest tests.unit.test_n8n_client tests.unit.test_support_chat_state -q
.venv/bin/reflex compile --dry
```

Com Playwright disponível, `tests/integration/n8n_chat_browser.py` exercita a UI
real interceptando a ponte com respostas simuladas, sem chamadas ao n8n/Xano.
Aceita `--url` e `--chromium`. `support_chat_browser.py` mantém a entrada antiga.

`tests/integration/n8n_bridge_smoke.py` exercita o ciclo real navegador/Reflex.
Envia somente uma pergunta genérica, sem login. Se o backend tiver segredo válido,
pode executar o workflow real e consumir IA. Não imprime o conteúdo da resposta
nem credenciais. Resultado de ponte OK com resposta de sucesso False não comprova
que a produção do n8n está configurada: apenas que o erro voltou ao painel.

Após alterações em produção, seguir a skill de gerenciamento de processos,
identificar a porta no log e reiniciar o backend; não parar processos de navegador.

## Aparência compartilhada

O diálogo global do assistente usa os tokens --vt-* definidos pelo tema do
sistema. Painel, histórico, mensagens, ações e campo acompanham a preferência
clara/escura antes da abertura e enquanto a janela está aberta, em todos os
perfis e páginas. Não há preferência separada do chat nem alteração no transporte.

A janela aberta do chat tem traço verde luminoso com halo em percurso de oito:
alterna a volta do cabeçalho/banner com a volta das mensagens/rodapé, passando
pela divisória inferior do banner. O ciclo é linear (6s; 12s em movimento reduzido).
Um ResizeObserver mantém o caminho SVG alinhado ao tamanho real do painel e banner.
O SVG decorativo é único por janela, não recebe foco ou cliques e acompanha os
cantos arredondados do painel em desktop e celular. Ao fechar/minimizar, a animação para.
O efeito é global e independente de autenticação ou perfil.

O painel abre acima da tartaruga, que continua visível e clicável. O restante da
página escurece enquanto o chat está aberto; clicar no fundo, na mascote, nos
controles ou pressionar Escape fecha o painel. Abertura e fechamento têm fade e
leve deslocamento, desativados pela preferência de movimento reduzido.

O banner `assets/gifturtle.mp4` permanece abaixo do cabeçalho e fora da rolagem
das mensagens e do histórico. Ocupa toda a largura na proporção original 16:9,
sem recorte; reproduz automaticamente, sem som e em loop. Fechar pausa o vídeo;
reabrir retoma. A altura do chat é limitada pelo espaço acima da mascote para
manter o painel e o campo de envio dentro da viewport.
