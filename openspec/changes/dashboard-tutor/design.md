## Context

Ver [proposal.md](./proposal.md) e os requisitos em `specs/tutor-dashboard/spec.md` e `specs/authenticated-navigation/spec.md`.

A navegação atual do tutor mantém `/` para a área/lista de pets e `/prontuario` para início e seções clínicas. A entrada Dashboard existe visualmente na sidebar, mas está desabilitada. `State.pets` já projeta pets próprios com foto, espécie, raça, nascimento e peso; o carregamento clínico atual solicita histórico e consultas para um pet por vez. A API de consultas e o histórico validam a propriedade do tutor no backend. O Dashboard geral, portanto, não deve consultar APIs clínicas repetidamente por pet nem reaproveitar o seletor do prontuário como estado de filtro.

Os registros disponíveis não incluem unidade explícita do peso, histórico de pesagens, compromisso futuro de exame ou evidência de que os dados do sistema representam todos os cuidados feitos pelo animal. O Dashboard somente projeta dados existentes e cálculos simples derivados de datas.

## Goals / Non-Goals

**Goals:**
- Disponibilizar o Dashboard em uma rota própria para tutor, mantendo a rota atual de Meus Pets e o fluxo clínico sem mudança de destino.
- Manter um escopo visual independente entre “Todos os pets” e um pet próprio, sem alterar a seleção clínica.
- Fornecer resumos compactos por animal e um perfil individual com dados cadastrais e históricos existentes.
- Proteger as leituras agregadas no backend pela identidade do tutor e propriedade dos pets.
- Comunicar datas e estados do registro sem inferir saúde, execução externa, atraso de exame ou cuidados completos.

**Non-Goals:**
- Criar registros clínicos, notificações, eventos de agenda de exames, unidade de peso ou histórico de pesagens.
- Implementar capacidades ainda indisponíveis na interface, incluindo Exames como destino de navegação.
- Criar dashboard de veterinário, clínica ou administração, gráficos analíticos, exportação ou novos perfis.

## Decisions

### Rota de Dashboard separada

Adicionar um destino tutor `/dashboard`, habilitando o item de navegação existente como destino distinto de Prontuário. Manter `/` e a seleção explícita de pet no fluxo atual. Isso reduz risco de quebrar a entrada existente e mantém separadas as funções: Dashboard resume; Prontuário apresenta registros clínicos completos.

Alternativa considerada: substituir a página `/` pelo Dashboard. Não escolhida porque `/` já é usado para Meus Pets e pelo fluxo de tutor autenticado; trocar seu significado afetaria essa navegação e poderia misturar os escopos.

### Escopo do filtro pertence somente ao Dashboard

Manter no estado da sessão um identificador de escopo do Dashboard (`todos` ou ID de pet pertencente ao tutor). A lista de opções deriva de pets retornados pela listagem autenticada existente. Alterar o filtro atualiza a apresentação do Dashboard, sem chamar a seleção de pet do prontuário, alterar a URL clínica ou reutilizar o contexto clínico como autorização.

Alternativa considerada: reaproveitar `selected_pet_id`. Não escolhida porque essa seleção controla carregamento e autorização de seções clínicas; o filtro geral precisa poder representar “Todos os pets” sem invalidar ou trocar aquele contexto.

### Leituras do Dashboard limitadas por pet e finalidade
Usar o endpoint autenticado `GET tutor/dashboard?pet_id=<id>` para carregar um pet por chamada. No modo “Todos os pets”, o frontend solicita o resumo de cada ID presente na lista autenticada de pets do tutor, com concorrência limitada a quatro chamadas. No modo individual, solicita novamente somente o pet selecionado. O filtro do cliente escolhe o contexto da leitura, mas nunca concede acesso: o endpoint chama `Clinical/assert_owner` com `pet_id` e `$auth.id`; uma ausência retorna “Pet não disponível”.

Cada consulta clínica também faz join com `pet` e exige `pet.tutor_id == $auth.id` e o ID do pet autenticado. As leituras retornam apenas os campos usados na projeção do Dashboard. Os conjuntos são limitados antes de chegar ao cliente: uma próxima consulta e um próximo retorno, até três consultas recentes por cada campo de data legado/atual, até uma próxima vacina, até três vacinas recentes, e até dez itens exibíveis de cada categoria de acompanhamento (retorno, vacina com data registrada ultrapassada e exame solicitado sem realização). Para as três categorias de acompanhamento são buscadas até onze linhas; a décima primeira serve somente para informar à interface que a lista foi limitada. Datas futuras são filtradas e ordenadas no Xano, enquanto consultas/vacinas recentes são ordenadas pela data relevante, evitando que um limite de histórico arbitrário esconda a próxima data. O arquivo fica em `xano/api/clinical/tutor/dashboard_GET.xs`, sob o grupo `Clinical`, e usa a função de propriedade `Clinical/assert_owner` já existente.

O endpoint não retorna rascunhos, diagnósticos, observações clínicas, resultados de exames ou dados de outro tutor. Uma falha em qualquer leitura da visão geral mantém o Dashboard em erro, em vez de apresentar um conjunto parcial como completo. O total de chamadas no modo geral cresce com o número de pets, mas cada leitura clínica permanece limitada por pet; a concorrência do cliente é limitada para evitar rajadas.

Alternativa considerada: uma única consulta agregada com limite global para todos os pets. Não escolhida porque um tutor com histórico grande poderia ocupar o limite e esconder os eventos de outro pet. A antiga leitura sem limite por categoria também foi descartada porque fazia a resposta crescer junto com todo o histórico.

### Projeções e status sem inferência clínica

- Perfil individual: foto acessível, nome, espécie, raça e idade calculada a partir de `data_nasc`; se ausente/inválida, idade não informada. Peso usa o valor atual cadastrado, sem adicionar unidade ou tendência.
- Próxima dose: menor `data_prox_dose` futura cadastrada. Datas em ou antes de hoje podem aparecer como item para acompanhamento, identificando explicitamente a data registrada.
- Consulta mais recente: registro finalizado com a data clínica disponível mais recente; consultas agendadas e em andamento não são tratadas como consulta concluída.
- Próximo evento: menor data futura entre consulta agendada, `retorno_previsto` e `data_prox_dose`. Exibir seu tipo; retorno permanece previsão e não vira agendamento. Exame não entra nessa lista porque o modelo atual não tem data futura de execução.
- Acompanhamento: sinalizar datas de vacina/retorno anteriores a hoje como datas registradas ultrapassadas; sinalizar exame solicitado sem realização registrada sem chamá-lo de atrasado. Hoje é apresentado como “previsto para hoje”/“retorno previsto para hoje”, não como vencido.
- Sem indicadores: usar texto estritamente limitado aos registros consultados, sem “saudável”, “em dia” ou “sem necessidade de cuidados”. Falha de leitura tem estado próprio e nunca se converte em estado vazio.
- Prévia: até três consultas finalizadas e três vacinas mais recentes, em ordem decrescente pelas datas disponíveis; não duplicar o histórico completo nas seções clínicas.

Alternativa considerada: um selo binário “saudável/pendente”. Não escolhida porque a ausência de registro não prova ausência de necessidade e uma solicitação de exame não tem prazo conhecido.

### Ações rápidas reutilizam destinos existentes

O modo individual liga ao Prontuário e Vacinas usando rotas/seções atuais e abre o agendamento existente com o pet desejado como contexto inicial, mantendo confirmação explícita pelo tutor. No modo geral, cada cartão identifica qual pet será usado ao iniciar uma ação. Nenhum atalho de Exames é criado enquanto o destino da interface permanecer desabilitado.

### Ciclo de leitura e privacidade

Carregar pets e resumo quando o tutor entra no Dashboard; atualizar ao trocar o escopo do Dashboard ou por ação explícita de atualizar. Não fazer polling. Aplicar gerações/identidade de sessão para descartar respostas atrasadas após logout, troca de sessão ou escopo. Manter dados clínicos no estado de servidor existente, sem persistência no navegador.

A autorização de propriedade é sempre validada no Xano, incluindo consultas agregadas. O filtro da interface é apenas apresentação, nunca controle de acesso. As regras de auditoria existentes para operações veterinárias permanecem inalteradas; esta proposta não cria logs, eventos de auditoria ou acesso administrativo novos.

## Risks / Trade-offs

- [A consulta “Todos os pets” realiza uma solicitação por animal] → Limitar cada consulta clínica no backend, limitar a quatro chamadas concorrentes e verificar tempo/volume com vários pets; não puxar o prontuário inteiro para cada cartão.
- [Uma falha parcial pode parecer ausência de pendências] → A leitura agregada deve ser tratada como unidade: erro não confirmado impede declarar resumo completo; exibir erro e permitir repetição.
- [Datas antigas podem refletir cuidados feitos fora do VetTech] → Rotular como “data registrada ultrapassada” e não afirmar que vacinação/retorno não ocorreu.
- [A lista de pets pode conter foto opcional ou URL inacessível] → Tratar foto como opcional e exibir fallback visual sem inventar dados cadastrais.
- [Peso pode ser interpretado em unidade errada] → Não apresentar unidade até que exista convenção explícita no domínio.
- [Mudança do filtro pode ser confundida com seleção do prontuário] → Manter estados independentes, rótulo de escopo visível e teste de que nenhuma operação de seleção clínica é disparada ao filtrar.
- [Retorno previsto pode ser confundido com consulta confirmada] → Apresentar o tipo “Retorno previsto” separado de “Consulta agendada”.

## Migration Plan

1. Adicionar endpoint de leitura e validar tutor autenticado, propriedade dos pets, projeção mínima e erros em testes.
2. Compor Dashboard em rota própria, integrar filtro e ações sem substituir `/` ou alterar a seleção do prontuário.
3. Habilitar o item Dashboard da navegação do tutor e validar estados vazios, erro, dados mistos e layout responsivo.
4. Em rollback, retirar o destino/rota e chamada agregada; preservar as tabelas e registros clínicos, que não são alterados por esta entrega.

Não há migração de dados nem mudança de schema prevista.

## Open Questions

Nenhuma questão aberta que altere os requisitos ou a abordagem. A unidade de peso permanece deliberadamente não exibida enquanto não for definida no domínio.
