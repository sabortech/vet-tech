# Verificação da fundação clínica

## Resultado final — 2026-10-22

**17/17 tarefas concluídas.** Publicação aplicada em Xano de desenvolvimento
confirmado pelo usuário, preservando e-mail único entre perfis e os fluxos existentes.

- 11 cenários normais cobertos: 8 de identidade/invariantes/pets e os 3 de acesso
  repetidos após a correção localizada dos endpoints de imutabilidade.
- 1 cenário adicional de atores inválidos e 1 de falha real de auditoria passaram.
- Login existente passou pela API e pelo Chromium: perfil do tutor, listagem do
  próprio pet e WebSocket na porta 3000. O servidor existente foi mantido.
- 41 testes unitários passaram; `reflex compile --dry` passou; 66 arquivos
  XanoScript válidos no validador oficial; OpenSpec estrito e diff sem erros.
- Todos os registros preexistentes preservados. Os 9 logs antigos receberam
  somente o horário já comprovado em `ocorrido_em`, sem inventar timestamps.
- Os 75 artefatos originais permanecem no workspace; 9 originais foram alterados
  na lista revisada. Login/cadastro, agenda, rascunho e finalização não foram
  substituídos. Os 15 artefatos novos completam 90 documentos publicados.

| Evidência | Resultado |
|---|---|
| [Invariantes e identidade](evidence/integration-normal.jsonl) | 8 cenários passaram antes da interrupção nos endpoints de logs |
| [Imutabilidade, histórico e revogação](evidence/access-regression.jsonl) | 3 cenários passaram após a correção, saída 0 |
| [Atores inválidos](evidence/identity-negative.jsonl) | Passou, saída 0, sem escrita ou log de sucesso |
| [Falha real de auditoria](evidence/audit-failure.jsonl) | Passou, rollback de consulta/exame e negativa de leitura/exportação |
| [Preservação dos registros](evidence/preservation-summary.txt) | Todos os registros anteriores comparados por ID e campos |
| [Artefatos publicados](evidence/published-artifacts.json) | Alterações limitadas ao conjunto revisado; auditoria restaurada |
| [Regressão do login](evidence/login-regression.txt) | API e interface passaram |

A execução monolítica da fase normal que detectou HTTP 200 na negativa de logs
não é relatada como sucesso completo. Depois da correção de apenas PATCH/DELETE,
o mesmo bloco de testes afetado e os passos subsequentes foram executados pela
fase `access-regression`, completando a cobertura sem repetir os oito cenários
já aprovados. Os comandos e o preparo estão em `docs/record-foundation-verification.md`.

As fixtures são sintéticas, com e-mails distintos e autorizações revogadas ao fim;
consultas, exames e logs de teste permanecem como evidência no desenvolvimento.
Nenhuma senha de conta existente foi usada ou alterada. Esta entrega cobre a
fundação de backend; as novas telas clínicas seguem o roadmap próprio.

As seções iniciais preservam o histórico das etapas parciais. A continuação
autorizada e suas evidências estão no fim deste documento; premissas antigas
sobre ausência de ambiente ou política de login foram substituídas.

## Histórico da aplicação parcial

## Entregue

- Configuração compartilhada obrigatória `XANO_API_BASE_URL`, sem fallback remoto.
- Validação no lifespan ASGI registrado na aplicação: imports e compilação continuam
  possíveis sem configurar o backend; startup sem configuração falha explicitamente.
- `.env.example` fictício e arquivos de ambiente locais ignorados pelo Git.
- Transporte HTTP testado com JSON, multipart, token, resposta vazia, erro de
  domínio, erro arbitrário, resposta inválida, timeout e falha de conexão.
- Mensagens arbitrárias e causas de transporte não expõem dados sensíveis.
- README atualizado; contratos, lacunas e migração preservando histórico em
  `docs/backend-foundation.md`; proposta/design reconciliados com código existente.

## Verificações locais

- `python -m unittest discover -s tests/unit`: 36 testes passaram.
- `reflex compile --dry`: compilação concluída.
- `openspec validate --all --strict`: 8 itens aprovados, sem falhas.
- `git diff --check`: sem erros.
- Startup válido/inválido exercitado no lifespan com ambiente sintético, sem rede.
- Perfil exercitado contra mock HTTP em localhost, sem conexão Xano real.

## Pendências que impedem conclusão

As tarefas 2.2–2.4, 3.2–3.3, 4.1–4.3 e 5.3 permanecem abertas por
dependerem também de verificação e integração no Xano de desenvolvimento.
Não há validação remota de invariantes, autorização veterinária ou auditoria.
Não houve publicação de endpoints nem migração de dados.

A política para pessoa/e-mail com dois perfis foi definida nesta continuação,
com autorização do usuário para resolver as decisões e continuar. Cada perfil
é autenticado por sua senha e tabela de domínio. Não há concessão de perfil
por campo do cliente nem uso da tabela genérica `user`.

As verificações remotas exigem ambiente Xano de desenvolvimento e fixtures
isoladas de dois tutores, pets e veterinários; nenhum acesso/configuração desse
ambiente foi confirmado nesta aplicação. Os testes locais não comprovam
segurança de endpoints remotos nem permitem marcar essas tarefas como concluídas.

Arquivamento não realizado e continua condicionado à aprovação do usuário,
depois da implementação e das verificações pendentes.

## Continuação em 2026-10-20

Implementados localmente:

- `Authentication/profiles/login`: credenciais verificadas separadamente por
  domínio, tokens vinculados a tutor/veterinário e resposta com os perfis
  comprovados; revisão do fluxo confirma que nenhum `perfil` enviado pelo
  cliente é usado para conceder acesso. Decisão e limites documentados.
- Grupo `vettech-records`: consentimento por dono, leitura de histórico,
  exportação JSON, registro de consulta/exame e consulta de logs pelo dono.
- Funções reutilizáveis `records/require_owner`, `require_access`,
  `validate_exam` e `audit`; operações clínicas e auditoria na mesma transação.
- Consulta com pet/veterinário obrigatórios, exame com pet obrigatório e
  consulta opcional compatível, raça com espécie obrigatória e log com
  timestamp, ação e vínculos obrigatórios. Índices únicos de e-mail/CRMV
  veterinário e do par pet/veterinário no consentimento.
- Negativa explícita de alteração/exclusão de logs nas APIs da aplicação;
  nenhuma permissão administrativa concedida ao frontend.
- Comando remoto reproduzível `tests/integration/run_record_foundation_live.py`,
  com fases normal/falha de auditoria; preparo e preservação de fixtures em
  `docs/record-foundation-verification.md`.

Verificações realizadas nesta continuação:

- 39 testes unitários passaram, incluindo guardas contra execução inadvertida
  do harness em produção e contra exposição de resposta sensível em erro.
- `reflex compile --dry`: passou.
- Validador oficial `@xano/developer-mcp` (language server): 55 arquivos XanoScript
  válidos, sem erros de sintaxe. Isso não comprova execução no Xano.
- Harness remoto: `--help` funciona; sem arquivo de fixtures encerra com código
  2 e mensagem acionável, sem usar configuração alternativa nem executar rede.
- Interface exercitada com Chromium e mock HTTP local, sem conexão ao Xano.

Tarefas 3.1 e 5.1 concluídas: contrato de identidade definido/implementado e
revisado, comando de integração e preparo documentados. As tarefas cuja definição
inclui integração real continuam abertas, embora tenham implementação local.
Não foi encontrado `XANO_CONFIG`, variável de ambiente Xano ou perfil em
`~/.xano/credentials.yaml`; não há arquivo de fixtures configurado. Não houve
publicação de endpoints, migração ou ensaio de rollback/autorização remotos.

## Retomada com Xano configurado em 2026-10-21

- Perfil CLI e leitura de workspace/branch/artefatos confirmados.
- 75 artefatos remotos lidos em cópia de trabalho temporária, sem sobrescrever
  a árvore do repositório. A prévia original removeria campos remotos e foi
  rejeitada antes de qualquer push.
- Schemas relevantes reconciliados preservando campos e índices remotos.
- Segunda prévia limitada: 5 tabelas ajustadas, 4 funções novas, 1 grupo de API,
  11 endpoints novos e 2 atualizados, sem DROP_FIELD. A conversão restante de
  `log_acesso.data_hora` é em tabela vazia segundo o inventário remoto.
- Inventário sem exposição de registros: consultas/exames/consentimentos/logs
  vazios; 3 pets e 41 raças sem vínculos nulos nos campos inventariados.
- Leitura adicional do histórico ajustada para excluir consultas em rascunho
  e exames delas, e para selecionar somente campos públicos da consulta.
- Transações novas alinhadas ao bloqueio por pet existente no backend remoto.
- Nenhuma publicação, migração de dados ou integração de escrita foi executada.
  Sandbox recusado pelo plano gratuito; workspace adicional recusado com 403;
  somente branch ativa disponível. A confirmação do ambiente de desenvolvimento
  foi solicitada ao usuário.
- Política de e-mail e login remota difere da premissa local; não foi substituída
  por um novo login sem reconciliar o contrato.

## Correções do login arquivadas separadamente

O diagnóstico de conexão, o teste positivo com fixture, a consulta da identidade
e o tratamento seguro de HTTP 429 foram consolidados, por solicitação do
usuário, na change arquivada
[`corrigir-conexao-e-feedback-login`](../archive/2026-10-21-corrigir-conexao-e-feedback-login/verification.md).
A antiga tarefa adicional 1.5 foi transferida para esse registro concluído;
não foi descartada nem adiada. A fundação mantém suas 17 tarefas originais
e as integrações clínicas ainda pendentes.

## Continuação autorizada em 2026-10-21

O usuário confirmou que o workspace é de desenvolvimento e aprovou preservar
e-mail único entre perfis. Essa decisão substitui a proposta histórica de
`profiles/login`; o contrato adotado é `Authentication/acesso/login`, com reserva
de e-mail e token por domínio. O login existente de tutor não foi substituído.

O inventário atual encontrou 4 tutores, 2 veterinários, 6 reservas de e-mail,
5 pets, 2 consultas, 0 exames, 9 logs, 1 consentimento, 41 raças e 2 espécies.
Foi guardada cópia privada anterior de dados/artefatos fora do Git. Todos os
vínculos obrigatórios inventariados estavam preenchidos. A prévia excluiu
remoção de campos/objetos e preservou os fluxos clínicos já publicados.

Publicados 24 artefatos revisados com `--transaction`: 5 schemas, 4 funções
novas, 2 funções existentes, 1 grupo e 12 endpoints (10 novos, 2 de pets atualizados).
Nenhum endpoint de login/cadastro, agenda, rascunho ou finalização foi substituído.
`Clinical/assert_access` reutiliza a política da fundação; `Clinical/audit`
preenche também `data_hora`, mantendo seu contrato e `ocorrido_em`.

Migração de log em duas etapas: timestamp inicialmente opcional, preenchimento
dos 9 valores nulos a partir dos horários confiáveis de `ocorrido_em`, depois
obrigatoriedade e padrão para novas operações. Cada log foi comparado campo a
campo: apenas `data_hora` foi preenchido, sem inventar horário ou alterar ação,
autoria, pet e conteúdo anterior. A primeira tentativa PATCH retornou 404 sem
escrita; a especificação OpenAPI da instância confirmou PUT e a migração passou.

Quatro novas identidades sintéticas, com e-mails distintos, e dois novos pets
foram preparados pelas APIs públicas. Nenhuma senha de usuário existente foi
usada ou alterada. Os resultados finais das fases de integração seguem abaixo.

### Evidências da publicação e preservação

- `evidence/published-artifacts.json`: 75 artefatos originais preservados, apenas
  9 originais alterados dentro da lista revisada, mais 15 novos (90 no total).
  Nenhuma alteração em login/cadastro, agenda, rascunho ou finalização.
- Função de auditoria restaurada, confirmada por novo pull; nenhuma API/função
  pública de alteração/exclusão de `log_acesso` encontrada.
- `evidence/preservation-summary.txt`: comparação por ID e por campo de todos
  os registros preexistentes; única mudança histórica deliberada é o preenchimento
  de `data_hora` nos 9 logs. Nenhum bloqueio clínico residual.
- `evidence/audit-failure.jsonl`: falha real injetada somente para o pet sintético,
  leitura/exportação/consulta/exame rejeitados e estado/logs comparados antes/depois.

A primeira expectativa de exame avulso exigia `null` na saída; a persistência
Xano representa o tableref vazio como `0`. O teste passou a aceitar a ausência
nessas duas representações, sem aceitar consulta inválida ou de outro pet.
Uma execução posterior foi interrompida por HTTP fora do contrato no início
da etapa de pets; cadastro e listagem passaram isoladamente. A suíte final é
executada sem consultas administrativas concorrentes e sem retentativas automáticas.
Não foi estabelecida a causa daquele status; ele não foi contabilizado como sucesso.

Os artefatos locais de identidade foram alinhados aos já publicados: cadastro
de tutor reserva o e-mail; funções e tabelas auxiliares de identidade veterinária
foram trazidas do workspace. Esses arquivos não foram republicados ou modificados
no servidor; servem para evitar que uma cópia local antiga reintroduza a política
anterior. O contrato local alternativo `profiles/login` foi removido.

### Correção encontrada pela integração de imutabilidade

A fase normal completou os oito primeiros cenários, incluindo todos os vínculos
e isolamento de pets, mas foi interrompida na primeira tentativa veterinária de
PATCH no log: o `throw` retornou HTTP 200 no Xano, sem executar mutação de dados.
Isso não satisfazia o contrato de negativa. Os dois endpoints novos PATCH/DELETE
foram corrigidos para `precondition (false)` com `error_type = "accessdenied"`,
validada sintaticamente e publicada em transação após prévia de apenas 2 updates.
O bloco afetado e os cenários subsequentes são repetidos pela fase
`access-regression`, que reutiliza o mesmo código da fase normal. Os oito casos
anteriores não foram declarados como uma execução completa da fase normal.

### Encerramento da integração

A fase `access-regression` terminou com saída 0: todos os quatro atores foram
impedidos de PATCH/DELETE, o log original permaneceu igual, o histórico legado
continuou operacional com timestamp, e a revogação negou imediatamente leitura,
escrita e exportação com o mesmo token, mantendo o segundo veterinário autorizado.
`identity-negative` terminou com saída 0; histórico e logs permaneceram iguais.
O Chromium confirmou o login e a listagem de pet do tutor sintético, sem iniciar
instância alternativa ou alterar a porta do aplicativo. A tarefa 5.3 foi marcada
concluída depois de reconciliar as evidências com o roadmap.
