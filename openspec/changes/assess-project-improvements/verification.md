# Verificação da aplicação parcial

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
