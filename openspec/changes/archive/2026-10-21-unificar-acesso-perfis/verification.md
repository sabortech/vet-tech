# Verificação de unificar-acesso-perfis

## Inventário somente de leitura

Em 20/10/2026 UTC, `scripts/profile_migration_inventory.py` consultou o Xano pelo perfil CLI configurado. Todas as operações remotas foram GET. Resultado: 3 tutores, 0 veterinários, 0 clínicas, 1 espécie, 1 raça e 3 pets; nenhum conflito de e-mail ou registro profissional identificado. Os três campos de hash de tutor estavam disponíveis. Nenhum registro remoto foi criado ou alterado.

Snapshot integral, metadados, plano de reservas e digests por registro estão no diretório privado ignorado `.venv/profile-migration/20261020T235930688138Z/`. Não versionar esses arquivos. A inspeção não comprova estabilidade do banco até a implantação: repetir e comparar sob suspensão de cadastros antes do backfill.

Quatro testes unitários do inventário passaram: conflito de e-mail entre tabelas, rejeição de dados profissionais incompletos sem inventar UF/vínculos, preservação de IDs/hashes e rejeição de clínica inexistente. O plano é apenas simulação, não executa migração. Restaurar somente a partir de backup privado verificado, preservando IDs e hashes, sem truncamento ou rehash de credenciais.

## Estado da implementação

Implementação e verificações das demais tarefas em andamento. O workspace principal ainda não recebeu novos schemas, APIs ou dados.

## Verificações locais

- 43 testes unitários aprovados, incluindo cadastro profissional sem autenticação automática, confirmação de identidade, descarte de resposta após logout, validação CRMV/UF e preservação do pet ao manipular menu/modal.
- `reflex compile --dry` aprovado em duas execuções com Reflex 0.9.11.
- A simulação do workspace principal detectou uma divergência antiga em `exame`; essa tabela foi excluída explicitamente do plano de publicação da change.

## Ambiente isolado

Criado tenant efêmero `exzz-vnfz-d7fe`, com expiração automática em 21/10/2026 02:08 UTC. A importação XanoScript foi transacional e sem cópia de registros pessoais; o CLI confirmou publicação somente nesse tenant.

O endpoint de opções retornou exclusivamente IDs/nomes. Cadastros reais de tutor e veterinário sem clínica concluíram nesse ambiente, com espécies e especialidades associadas. O teste seguinte encontrou projeção incompleta de campos internos na consulta da reserva durante o login; corrigida localmente com `output` explícito, pendente de nova execução integrada.

APIs administrativas de tabela/função com `X-Tenant` retornaram HTTP 500 nesse cluster. As funções e rotas auxiliares de teste foram geradas exclusivamente no bundle ignorado `.venv/shared-profile-test-backend/`; as rotas exigem segredo aleatório privado e nunca integram `xano/` ou a publicação principal. Elas manipulam somente fixtures sintéticas. Nenhuma aprovação de concorrência, rollback ou navegador deve ser inferida dos testes locais.

## Suíte integrada do backend aprovada

Após corrigir a projeção e substituir a variável reservada de resposta por `login_result`, a suíte real passou em 10 cenários: projeção pública de opções; cadastro dos dois perfis com clínica opcional; login e confirmação de identidade com IDs coincidentes; rejeição de tokens cruzados e perfil forjado; credenciais inválidas/ausência de token; duplicidade cruzada de e-mail; rollback da reserva e identidade após falha de unicidade do CRMV; dados profissionais e vínculos inválidos; disputa concorrente de e-mail com exatamente um vencedor; contrato legado de login tutor preservado.

A execução respeita HTTP 429 com espera limitada, repetindo apenas rejeições explícitas por limite; não repete POST de resultado incerto. Credenciais inválidas retornam HTTP 403 nesse Xano, enquanto ausência/token de outra entidade retorna 401. As credenciais de fixtures ficaram exclusivamente em arquivo ignorado. Esses resultados são do tenant temporário; a publicação principal e a QA visual ainda não foram realizadas.

## Navegador aprovado

`run_shared_profiles_browser.py` passou com Chrome headless, servidor Reflex em produção/single-port na porta 8011 e backend real selecionado por `XANO_TENANT`. Sem mocks de resposta. Verificados: modal com Escape/retorno de foco e descarte do rascunho; cadastro real de dois pets SRD; escolha por teclado; preservação do pet ao recolher menu e após cadastrar outro; troca de pet; seção clínica identificada como indisponível; logout e login veterinário sem dados herdados; cadastro veterinário real sem clínica e login posterior. Desktop 1280×900 e celular 390×844 sem overflow horizontal; nenhum erro JavaScript.

Capturas em `.venv/shared-profile-browser-qa/` foram inspecionadas em desktop, celular e cadastro. Os percursos independentes aguardam a janela do plano Xano. Checkboxes controlados pelo servidor são verificados após a resposta do estado, não imediatamente no mesmo clique. As fixtures continuam apenas no tenant de teste até a limpeza final.

## Implantação e integridade

O inventário foi repetido em `.venv/profile-migration/20261021T010858219310Z/`: todos os digests dos seis conjuntos originais coincidiram com o primeiro snapshot. O bundle de migração suspendeu os dois cadastros pela função compartilhada, mantendo login tutor legado disponível. A publicação foi transacional e excluiu `table/exame.xs`.

O dry-run do backfill indicou exatamente 3 reservas e 5 especialidades ausentes, sem escrita. A aplicação confirmou a suspensão na fonte publicada, criou somente essas oito entradas e comparou novamente todos os digests originais, com resultado preservado. Manifestos privados em `.venv/profile-migration/backfill-20261021T011221715623Z/` e `backfill-20261021T011257060624Z/`. Em seguida, somente a função compartilhada foi atualizada para reabrir os cadastros. GUIDs atribuídos pelo Xano foram incorporados aos artefatos autoritativos.

`run_shared_profiles_smoke.py` passou no workspace principal: projeção do catálogo publicado, cadastro/login/me dos dois perfis, rejeição de tokens cruzados, negação de pets ao veterinário e contrato tutor legado. Criou duas contas fictícias, removeu seus vínculos e reservas e confirmou igualdade integral dos registros anteriores. Resultado sem PII em `smoke-result.json`: permanecem 3 tutores, 0 veterinários, 0 clínicas, 3 pets, 1 espécie e 1 raça; as adições duráveis são 3 reservas e 5 especialidades.

Os testes adicionais de token de 1 segundo expirado e ambiguidade histórica entre tabelas também passaram no tenant temporário, sem emissão de sessão para o e-mail ambíguo. As fixtures de identidade e pets da QA foram removidas. A última proteção de sessão também impede que a conclusão tardia da atualização da lista emita limpeza de arquivos no formulário de outra sessão; 44 testes unitários aprovados.

## Encerramento da verificação

45 testes unitários aprovados e compilação final aprovada. O envio do modal agora publica o estado ocupado antes de iniciar a chamada à API e recusa repetição enquanto ocupado; a verificação adicional com clique duplo no Chrome criou exatamente um pet e limpou a fixture ao terminar. Nenhuma resposta de sessão anterior emite limpeza de arquivos no novo contexto.

O procedimento de reversão foi ensaiado somente no tenant efêmero: suspendeu cadastro dos dois perfis com HTTP 403 e não modificou registros; a função final foi reaplicada, um cadastro fictício confirmou a reabertura e a conta foi removida. O workspace principal permaneceu aberto durante esse ensaio. O bundle de suspensão e o procedimento de restauração estão documentados, sem truncamento ou exclusão de dados anteriores.

A confirmação final no tenant efêmero encontrou tutores, veterinários, reservas e vínculos de fixtures vazios; o manifesto local de credenciais foi removido. O tenant expira automaticamente no horário registrado acima. O servidor local foi reiniciado com o código final e sem `XANO_TENANT`, em `http://localhost:8011`, ligado ao backend principal. A change fica implementada para revisão, sem sincronização/arquivamento automático das specs ou commit de Git.
