# Continuidade do assistente com veterinário

Para retomar a implementação e concluir o workflow n8n, seguir
[o contexto e roteiro de continuidade](retomada-chat-n8n.md).

## Contrato do n8n

A resposta atual preserva `ok`, `request_id`, `conversation_id`, `reply` e `error`.
Acrescentar opcionalmente:

```json
{
  "handoff": {
    "type": "veterinary",
    "reason": "Motivo resumido do encaminhamento"
  }
}
```

`reason` deve ter entre 1 e 1000 caracteres, sem tokens ou segredos. Não incluir
IDs de usuário, pet, profissional ou chamado nesse objeto. Sem encaminhamento,
omitir `handoff` ou devolver `null`. Texto livre em `reply` não cria chamado.
O workflow só deve propor encaminhamento para `user.authenticated = true` e
`user.role = tutor`. O aplicativo revalida identidade, pet e consentimento.

O bot propõe; o tutor confirma o pet e o compartilhamento. A criação efetiva
acontece pelo backend do aplicativo, nunca por um comando livre da IA.

## Operação

Após confirmação, o chamado entra na fila compartilhada. A fila expõe somente
identificador, estado e horários; o motivo, tutor e mensagens só aparecem após
um veterinário assumir. A transação impede dois responsáveis simultâneos.
O responsável é identificado por nome e CRMV/UF. O tutor e esse profissional
podem trocar mensagens, retomar e encerrar; o tutor pode cancelar enquanto aguarda.
Encerrados continuam somente leitura. Um novo atendimento exige nova conversa.

O controle Atendimentos no chat lista chamados próprios e, para veterinários,
a fila. Eventos persistentes alimentam avisos internos sem texto clínico.
Atualização do chamado ativo a cada vinte segundos; a fila atualiza por ação explícita;
fechar o painel não encerra o chamado. Conteúdo fechado não é mostrado a outra
identidade, e a participação é revalidada em cada solicitação ao backend.

`SUPPORT_CHAT_BRIDGE_SECRET` deve ter o mesmo valor privado no servidor Reflex
e no ambiente Xano. Ele protege a criação contra histórico forjado diretamente
na API e não é usado como autenticação do tutor: o token e a propriedade também
são obrigatórios. Payload e bridge_key são entradas sensíveis no Xano. Nunca
copiar valores para este documento, frontend ou registros técnicos.

Chat não concede nem revoga acesso ao prontuário; leituras e gravações clínicas
continuam no fluxo de autorização/auditoria existente. Não cria receitas,
diagnósticos, consultas ou agendamentos. Sem anexos, áudio/vídeo ou novo design.

## Verificação de desenvolvimento

```powershell
.venv/Scripts/python.exe -m unittest tests.unit.test_n8n_client tests.unit.test_support_chat_state tests.unit.test_support_client -q
.venv/Scripts/python.exe scripts/support_chat_smoke.py --development --run support-chat-20261111
.venv/Scripts/python.exe scripts/support_chat_access_smoke.py --development --run support-chat-20261111
.venv/Scripts/python.exe tests/integration/veterinary_support_browser.py --development --run support-chat-20261111 --url http://localhost:3002
.venv/Scripts/python.exe tests/integration/support_retention_browser.py --development --run support-chat-20261111 --url http://localhost:3002
.venv/Scripts/python.exe tests/integration/support_handoff_browser.py --url http://localhost:3002
node --test tests/unit/n8n_support_handoff.test.cjs
.venv/Scripts/python.exe tests/integration/n8n_handoff_smoke.py --run support-chat-20261111
.venv/Scripts/python.exe tests/integration/n8n_support_cycle_browser.py --development --run support-chat-20261111 --url http://localhost:3003
.venv/Scripts/reflex.exe compile --dry
```

O smoke remoto usa o perfil Xano `vetech`, workspace de desenvolvimento 167758,
e cria contas/pets exclusivamente sintéticos com ledger privado em
`.venv/clinical-smoke/<run>`. Não reutilizar dados reais nem publicar ledger,
respostas, tokens ou capturas. Os chamados sintéticos e seus eventos são
preservados para auditoria da verificação; não excluir tutores/pets referenciados
por esses chamados pelo cleanup clínico genérico.

Em 11/11/2026, a validação real das APIs confirmou criação idempotente, bloqueio
de pet alheio, consentimento obrigatório, bloqueio de contexto forjado sem
credencial privada, isolamento entre contas, fila mínima, disputa entre dois
veterinários, envio/retry sem duplicação, resposta humana, encerramento,
histórico persistente e rejeição de adulteração de eventos. O código Xano foi
publicado seletivamente, sem importar registros ou excluir tabelas existentes.

Também passaram as verificações reais no navegador de mensagens bidirecionais,
encerramento e retomada após fechamento, recarga e novo login, com isolamento ao
trocar de tutor. O teste de confirmação/cancelamento, avisos e retry da interface
usa ponte simulada e não aciona n8n/Xano; ele valida os controles e não a
publicação do workflow. Execute os testes reais em sequência, usando o mesmo
ledger em apenas um processo por vez para não disputar evidências nem a cota.

O contrato de encaminhamento foi publicado no workflow n8n; a versão ativa e
os testes diretos por perfil estão registrados em `n8n-chat.md`. O teste
`n8n_support_cycle_browser.py` usa o workflow publicado, confirma pet e consentimento
na interface e verifica disputa entre dois veterinários, retry de mensagem com
confirmação descartada, mensagens bidirecionais, retomada e encerramento. Esse
teste não prepara contexto pela API nem simula a resposta do bot. A injeção de
falha descarta somente a confirmação de uma gravação real; o retry passa pelo
Reflex e Xano existentes. Os resultados ficam no ledger privado, sem conteúdo
sensível na evidência pública.

## Fluxos do painel e consumo

A confirmação de encaminhamento é uma tela própria com pet e consentimento.
Ela usa `support_pets`: uma leitura autenticada de pets, sem listar tickets antigos.
Atendimentos anteriores aparecem somente ao abrir **Atendimentos**, em cartões,
e o conteúdo de uma conversa humana exige seleção explícita. **Nova conversa**
limpa o contexto da ponte e gera outro ID, sem encerrar tickets no servidor.

Falhas apresentam tentativa manual que conserva campos e identidade da operação.
Criação continua idempotente por conversation_id no Xano; envio e encerramento
preservam operation_id. Botões do formulário ficam bloqueados durante a operação.
Não há repetição automática de escritas. Falhas remotas de configuração ou
indisponibilidade ainda exigem correção no serviço correspondente.

O polling consulta apenas o ticket humano ativo a cada 20 segundos (antes 10),
suspenso em aba oculta, painel fechado, erro pendente e atendimento encerrado.
A lista atualiza somente por solicitação; o assistente não faz polling humano.
Isso reduz as leituras periódicas de cerca de 6 para 3 por minuto por painel ativo,
e zera essas leituras em estados ociosos. A seleção de pet elimina a antiga leitura
adicional de tickets. As duas requisições por pergunta/resposta no workflow n8n
continuam existentes: alterá-las exige revisar o workflow externo. Não há cache
compartilhado de mensagens ou credenciais entre usuários.

Verificação sem consumir Xano ou IA:

```bash
.venv/bin/python -m unittest tests.unit.test_support_chat_state tests.unit.test_n8n_client -q
.venv/bin/python tests/integration/chat_flows_browser.py
.venv/bin/reflex compile --dry
```

O teste de navegador aceita `--chromium /caminho/do/chrome`, simula a ponte e
registra screenshots em `openspec/changes/reorganizar-fluxos-chat/evidence/`.

Na lista, o título Atendimentos fica à esquerda e as ações Atualizar atendimentos
e Falar com assistente aparecem como botões compactos com ícones à direita,
na mesma linha, com nome acessível e descrição ao passar o cursor.

Se a credencial privada de criação faltar no servidor Reflex, o encaminhamento
retorna erro de configuração sem chamar o Xano nem oferecer retry como solução.
Restaurar no `.env` ignorado o mesmo valor já configurado no Xano e recarregar
o backend. Não gerar outro segredo só no frontend ou remover a validação.

Os cartões das listas do tutor e do veterinário usam vermelho para aguardando, amarelo para
em atendimento e verde para encerrado. Borda, status e ação acompanham a paleta
clínica, com rótulos textuais e contraste adaptado ao tema, sem novas consultas.

Durante a conversa humana, informações e ações ficam em um pop-up aberto pelo
ícone flutuante interno. O ícone segue a cor do status para tutores e veterinários.
Abrir usa o ticket já carregado, sem chamada extra. Escape, botão de fechar e
clique fora fecham o pop-up e devolvem foco ao ícone. O motivo permanece ao
fechar/reabrir no mesmo ticket; sair do fluxo ou trocar sessão limpa os detalhes.
O polling pausa enquanto o pop-up está aberto para preservar a edição; a ação
Atualizar atendimento continua disponível manualmente.

### Fotos nos atendimentos

Lista e pop-up exibem a foto cadastrada do pet em moldura circular com a cor
do status e fallback de patinha para foto ausente, inválida ou indisponível.
Support/operate usa o join de pet existente na listagem, projetando pet_id
e foto; pet_photos indexa imagens por pet para evitar repetir base64 em vários
chamados do mesmo animal. O detalhe autorizado inclui pet.photo. Não há consulta
extra por cartão. A fila veterinária mínima passa a incluir identificador/foto
do animal; tutor, nome do pet e conteúdo clínico continuam fora da fila antes
da assunção. Os filtros de propriedade/participação permanecem no Xano.

Verificação adicional sem serviços externos:

```bash
node --test tests/unit/support_pet_photos.test.cjs
.venv/bin/python tests/integration/support_pet_photos_browser.py
```

Cartões e fotos usam segmentos SVG luminosos no perímetro com a cor do status,
em movimento horário por CSS (6s; 12s com movimento reduzido), sem eventos
remotos nem interceptação de cliques. A foto do pop-up compartilha o efeito.

Mensagens humanas usam ícones de tutor (pessoa/coração) e veterinário
(estetoscópio), inclusive nas mensagens próprias; a mascote identifica o bot.
No atendimento, o cabeçalho do tutor mostra o profissional confirmado e o
status; o veterinário vê Conversa com tutor e o pet de contexto. Sem nome
profissional confirmado usa Atendimento veterinário. Voltar ao assistente
restaura nome/mascote originais. Essas mudanças reutilizam dados já carregados.

O LED da janela acompanha o status durante atendimento humano, inclusive
o halo; o pop-up de informações tem o mesmo perímetro animado contextual.
Fora do ticket, o LED da janela volta ao verde padrão do assistente.

A conversa humana usa a paleta do status em cabeçalho, navegação, envio,
ícones, campo, foco e balões; superfícies são suavemente tonalizadas e botões
sólidos usam texto escuro. O tema da página não é alterado.

### Emojis

Todos os compositores compartilham botão de emoji com painel local, busca
em português e categorias. A seleção insere no cursor ou substitui a seleção
sem enviar automaticamente, respeitando o limite de 1000 caracteres. Escape,
fechar e clique fora dispensam o painel; selecionar devolve foco ao campo.
O controle acompanha tema/status e fica desabilitado junto ao compositor.
Não usa biblioteca externa nem faz chamadas Xano/n8n para buscar/inserir emojis.

Verificação: `.venv/bin/python tests/integration/chat_emojis_browser.py`
(com `--chromium` opcional).

### Nomes dos participantes

O detalhe autorizado inclui tutor.name confirmado pela consulta do pet com
join de tutor; o nome profissional continua vindo do veterinário atribuído.
Não se acrescenta nome do tutor à fila nem campos pessoais extras. Cabeçalho
mostra o nome do interlocutor, com fallback Tutor/Atendimento veterinário.
Rótulos de perfil e nome ficam acima do avatar/balão, separados do corpo da
mensagem e inseridos como texto seguro. Não há request adicional por mensagem.

### Entrega e leitura das mensagens humanas

Mensagens próprias persistidas mostram Entregue (salvas no atendimento, sem
comprovar entrega a um dispositivo específico). Após o interlocutor visualizar
a mensagem no chat aberto, em aba e janela em foco, ela passa a Visto, com dois
checks azuis e horário de leitura disponível ao passar o cursor. Mensagens
antigas não recebem leitura presumida. O estado é armazenado em read_at por
mensagem no agregado existente, sem nova tabela ou evento por polling.

O navegador acumula a última mensagem recebida visível e envia read_through
em um get agrupado após cerca de 350ms, ou aproveita get/send/close já em curso.
Lotes adicionais respeitam intervalo mínimo de cinco segundos; trocar de aba
envia o marcador já observado, sem registrar novas visualizações na aba oculta. A transação revalida participação e
referência a uma mensagem recebida, marca as recebidas até ela e grava somente
se houver leitura nova. Repetições são idempotentes e não alteram o horário já
registrado. Painel fechado, aba sem foco/oculta, histórico, seletor de emojis
ou pop-up aberto não geram confirmação de visualização. A rolagem permanece
na posição atual durante atualizações de mensagens/recibos.

Mantém-se o polling de 20s para atualização contínua. Retornar ao chat faz
uma consulta agrupada de recibos, com uma reconferência limitada se ainda
houver mensagens próprias não vistas. A atualização depende da latência de
rede; o envio da leitura não espera mais o próximo ciclo de polling. Em encerrados, só
há uma sincronização se uma leitura nova estiver pendente; não há polling
contínuo para observar recibos, que serão atualizados ao reabrir/atualizar.

Os cartões próprios/atribuídos incluem nome do tutor pelo join existente; a
fila veterinária não assumida mantém tutor nulo, sem expor esse nome.

Verificações sem serviços externos:

```bash
node --test tests/unit/support_read_receipts.test.cjs
.venv/bin/python tests/integration/support_read_receipts_browser.py
```

Quando tutor.name está vazio no cadastro confirmado, o chat explicita Nome
não informado. Preencher o nome exige atualizar o cadastro do tutor; a
interface não inventa nomes. O recibo usa SVG compacto de um ou dois checks.

### Contatos do tutor para o profissional responsável

O detalhe veterinário autorizado inclui a seção Tutor responsável com nome,
telefone e e-mail cadastrados. Valores vazios aparecem como Não informado.
A projeção aproveita o join de tutor existente na consulta do pet e mantém
os guards de participação/propriedade; contatos não são enviados à fila
nem incluídos no detalhe do perfil tutor. Não inclui CPF, endereço ou credenciais.

### Editar e apagar mensagens humanas

Durante atendimento ativo, clicar no próprio balão, usar reticências ou Enter
com o balão focado abre Opções da mensagem. Editar permite salvar até 1000
caracteres e identifica a mensagem como Editada; apagar exige confirmação e
substitui o corpo por Mensagem apagada para os dois participantes. Mensagens
alheias, contexto do assistente e atendimentos encerrados não oferecem ações.

Xano valida participação e autoria por perfil/ID autenticados, além de revisão
numérica e estado. Operações edit/delete usam operation_id para retry exato;
revisão desatualizada não sobrescreve alteração posterior. O evento guarda o
texto anterior em value para auditoria privada, campo removido das respostas
públicas. A remoção é lógica: texto público fica vazio e metadados/auditoria
são preservados. O horário original permanece após edição.

Editar invalida read_at da versão anterior. read_revision evita confirmar
conteúdo novo por marcador coletado antes da alteração. O polling pausa no
editor e seu rascunho permanece em caso de falha; confirmação bem-sucedida
reutiliza a resposta da operação, sem consulta adicional para atualizar o balão.

Verificação sem alterar conversas reais:

```bash
node --test tests/unit/support_message_actions.test.cjs
.venv/bin/python tests/integration/support_message_actions_browser.py
```

As reticências abrem as opções; Editar mensagem mostra lápis e Apagar mensagem mostra lixeira dentro do pop-up.

### Prazo das mensagens e horário inicial

Editar/apagar vale até 10 minutos do envio original. O Xano calcula o prazo
com seu próprio relógio, sem aceitar data do navegador, e não renova o prazo
após edição. Retry exato já concluído permanece idempotente depois do limite.
O detalhe inclui server_time para referência visual monotônica: mudanças
no relógio do computador não reabrem a janela. Reticências continuam disponíveis e mostram aviso com opções bloqueadas
quando o prazo vence; editor aberto preserva texto para cópia.

O símbolo de círculo cortado fica depois de Mensagem apagada. Um único
horário HH:mm centralizado aparece no início da conversa; usa abertura local
no bot e criação do ticket no atendimento, sem duplicar nas atualizações.

### Exclusividade na fila compartilhada

Todos os veterinários elegíveis veem chamados aguardando. Support/operate
serializa assunção com lock único por ticket dentro da transação e revalida
status/participação: depois de atribuído, outro profissional não reassume
nem lê o conteúdo e deixa de ver o chamado na fila. Sem transferência
automática ou reabertura por outro médico.

Teste real restrito a fixtures sintéticas existentes de desenvolvimento:

```bash
.venv/bin/python scripts/support_claim_race_smoke.py --development --fixture-run <run-sintetico>
```

O teste cria somente um chamado sintético, disputa assunção com dois atores
sintéticos, verifica bloqueio de reassunção/leitura e retirada da fila e
encerra o chamado. Evidência e identificador ficam no ledger privado; não
excluir atores/pets referenciados pelo histórico preservado.

No cabeçalho, nome, perfil/ausência do nome, pet e status ficam em linhas
separadas. Nos cartões do tutor, o botão usa Ver conversa em todos os estados.
Abrir cartão não altera o responsável ou cria outro chamado.
