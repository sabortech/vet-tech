# Design

## Context

Motivação e escopo em `proposal.md`. Brief lido em `/home/usuario/Downloads/VetTech_OpenSpec_Exportacao_Consulta_PDF.md` (seção 13 prevalece: somente planejamento, sem código ou commit). Há uma cópia não rastreada em `docs/` preexistente a esta tarefa; não foi alterada. Evidências abaixo são do checkout local, não de publicação remota.

### Evidências do checkout

| Evidência | Observação e consequência |
|---|---|
| `AGENTS.md`, `docs/architecture.md`, `openspec/config.yaml` | Reflex + Xano, organização incremental, autorização no backend e português. OpenSpec instalado 1.13.2, schema `spec-driven`; nenhuma outra change ativa no início. |
| `requirements.txt`, `rxconfig.py`, `.venv` | Reflex 0.9.11, Python local 3.13.5, httpx instalado 0.28.1. Jinja2, WeasyPrint e ReportLab ausentes, inclusive na resolução instalada. Não foram encontrados manifesto Docker/deploy, pyproject.toml ou .python-version no inventário. Isso não prova capacidade do ambiente de hospedagem. |
| `components/clinical.py:130`, `consultation_detail()` / `tutor_consultations()` | Detalhe tutor já tem Voltar à lista, datas, motivo, diagnóstico, observações, ID do veterinário e complementos. Lista permite ler finalizadas e legados. Inserir botão aqui, sem nova página/rota nem alterar o atendimento veterinário. |
| `features/auth/state.py:87`, `features/clinical/state.py:155` | State autenticado já incorpora ClinicalMixin; adicionar evento ao mixin existente, sem outra sessão. |
| `features/clinical/state.py:717`, `fetch_tutor_clinical()` | Leituras paralelas de histórico e consultas via xano_request; `cards()` transforma valores em strings e estado ausente em `legado`. O PDF deve usar resposta bruta fresca, não textos/cache visual. |
| `features/clinical/state.py:817`, `show_consultation_detail()` | Seleciona consulta por ID de history_rows e complementos por consulta_id; isso é apresentação e não autorização. |
| `_session_generation`, `_clinic_generation`, `_clinical_current`, `_tutor_load_current` e limpeza em `ClinicalMixin` | Há padrões para invalidar contexto em logout e troca de pet; estender à consulta/detalhe e etapa de renderização. |
| `shared/xano_client.py::xano_request` | URL `{base}/api:{group}/{endpoint}`, bearer de servidor e X-Tenant opcional, timeout de 20 s, retries limitados de 429 em Clinical, erros sanitizados. Reutilizar sem cliente paralelo; nunca registrar headers. |
| `tutor_history_GET.xs`, `tutor_consultations_GET.xs` | GET tutor/pets/{pet_id}/historico e GET tutor/consultas?pet_id=..., auth tutor e assert_owner. Grupo versionado Clinical, alias usado pelo Python vettech-clinical. Não existe leitura genérica GET /consultas/{id} comprovada. Histórico não chama audit. |
| `function/clinical/history.xs` | Listas consultas, vacinas, medicamentos, exames, diagnosticos, doencas. Só consultas finalizadas ou sem status entram; complementos sem vínculo também entram no histórico geral. Exportação precisa restringir mais. |
| `function/clinical/assert_owner.xs` | Propriedade validada por pet.id e tutor_id do auth; retorna id, nome, especie_id, tutor_id. Nome do pet pode vir desta validação, sem novo endpoint de perfil. |
| `api/application_data_persistence/pet/get_GET.xs` | GET pets/{pet_id}, grupo Pet, auth tutor e proprietário; contém nome, sexo, nascimento etc. V1 não precisa duplicar esta leitura nem acrescentar dados pessoais. |
| `function/clinical/audit.xs`, `table/log_acesso.xs` | Audit aceita pet, veterinário, tutor, consulta, ação, operacao. Tabela já tem operacao com índice único. veterinario_id é campo não opcional na tabela: usar o responsável da consulta, mantendo tutor_id como ator explícito. Sem tabela nova. Validar comportamento no workspace antes de aplicar. |
| `api/clinical/audit_GET.xs` | GET tutor/pets/{pet_id}/auditoria lê logs próprios, inclui tutor_id/consulta_id/ação/data; não registra exportação. |
| `api/clinical/finish_POST.xs`, `booking_POST.xs` | Padrões existentes de db.transaction, chave de operação e auditoria no mesmo fluxo. Reutilizar abordagem e tratamento de conflito de unicidade. |
| `shared/dates.py::date_label/instant_label` | Data civil preservada; instantes formatados em America/Sao_Paulo, sem converter data clínica em instante. |
| `assets/vet_tech.css`, `assets/mascote_logo.png`, `assets/favicon.svg` | Identidade verde e assets reais. Nenhum template oficial de relatório ou fonte TTF/OTF foi localizado nos assets examinados; o logo do PDF não está aprovado. |
| `tests/unit/test_clinical_state.py`, `test_xano_client_clinical.py`, `tests/integration/consultations_browser.py`, `scripts/clinical_smoke.py` | Ampliar testes adjacentes e smoke em ambiente de desenvolvimento, sem infraestrutura paralela ou dados reais em fixtures versionadas. |

### Compatibilidade do download verificada localmente

Inspeção com `inspect.getsource(rx.download)` na venv confirmou `download(url=None, filename=None, data: str | bytes | Var = None, mime_type=None)`. Bytes são convertidos em data URI base64 e enviados no evento `_download`. Planejar `rx.download(data=pdf_bytes, filename=nome_validado, mime_type="application/pdf")`, sem URL pública e sem guardar bytes em State serializado. Base64 aumenta transporte/memória; aferir limite de tamanho e latência no deploy antes de habilitar. Esta descoberta é por leitura do pacote instalado, não por suposição da API atual na internet.

## Goals / Non-Goals

**Goals:** separar obtenção autorizada, DTO e renderização; reutilizar autenticação e contratos; conseguir verificar auditoria e isolamento sem dados de produção; permitir trocar layout sem mudar o cliente Xano.

**Non-Goals:** segunda autenticação, banco/tabela nova, PDFs persistidos, histórico completo, exportação veterinária, lote, envio externo, anexos binários de exames, assinaturas, nova clínica/CRMV ou migração de legados.

## Decisions

### 1. V1 tutor, finalizada e uma consulta por documento

A elegibilidade exige status bruto exatamente `finalizada`. Sem status não é prova suficiente de publicação para exportação; legados permanecem na tela, sem botão de exportar. O ID inteiro positivo deriva do detalhe atual e é revalidado no servidor. Não aceitar status, autoria ou payload clínico do navegador.

### 2. Nova operação de exportação no Xano, reutilizando o domínio

**Contrato proposto, ainda inexistente/não publicado:** `POST tutor/pets/{pet_id}/consultas/{consulta_id}/exportar`, grupo Clinical / alias vettech-clinical, auth tutor. Arquivo proposto `xano/api/clinical/export_consultation_POST.xs`. Entrada: IDs inteiros positivos e `operacao` UUID de uma tentativa lógica. Tutor ator é auth.id, nunca input.

No mesmo fluxo transacional: assert_owner; ler consulta pelo par pet/consulta; exigir finalizada; reutilizar Clinical/history para o pet e filtrar consulta e complementos estritamente por IDs; validar idempotência; registrar Clinical/audit antes de devolver o recorte. Resposta proposta: `{consulta, pet: {id, nome}, vacinas, medicamentos, diagnosticos, exames, auditoria_id}`. São campos do novo envelope, não alegação de JSON já existente. Não devolver tutor_id, rascunho, histórico inteiro ou condições consolidadas. Não criar genericamente GET /consultas/{id}, nem duplicar regras clínicas de publicação em outro serviço.

As leituras existentes permanecem na UI; a exportação usa a operação dedicada para eliminar o intervalo entre validação e auditoria de uma sequência de GETs + log independente. Não alterar inicialmente Xano nesta etapa de planejamento. Reutilização dos contratos versionados é conceitual por funções e seleção, sem tratar GET atual como auditoria suficiente.

Erros propostos: 401 sessão inválida; 404 genérico para pet/consulta ausente ou alheia; 409 consulta inelegível ou chave reaproveitada com outro alvo; 5xx falha interna/auditoria sem payload clínico. Mensagens novas precisam de inclusão explícita na política segura de xano_client, sem liberar mensagens arbitrárias.

### 3. Auditoria e retries sem persistir documentos

`acao=exportar_consulta`, tutor_id=auth.id, veterinario_id=responsável real, pet_id/consulta_id validados, timestamp servidor. O log significa **liberação autorizada dos dados para emissão**, não comprovação de arquivo salvo pelo navegador. Se renderização ou entrega falharem depois dessa liberação, o log permanece verdadeiro quanto à operação autorizada, sem afirmar download concluído. Negativas não geram log de sucesso; logs operacionais de negativa, se houver, não incluem conteúdo clínico e não criam nova trilha/tabela nesta V1.

Chave persistida proposta `exportar_consulta:<tutor_id>:<uuid>` em log_acesso.operacao. Guardar pet/consulta no próprio registro já existente e rejeitar mesma chave com alvo diferente. Revalidar acesso e status antes de qualquer replay. Índice único resolve disputa; tratar concorrência por conflito/releitura, sem dupla auditoria, verificando ator/ação/alvo antes de aceitar registro prévio. Resposta perdida reutiliza a mesma chave. Novo clique após sucesso gera nova chave. A operação do mesmo alvo pode reconstruir o recorte finalizado sem armazenar PDF; não promete um PDF binariamente idêntico em retries. Falha de auditoria impede resposta de dados; falha de transporte sem confirmação não autoriza gerar a partir do cache da UI.

### 4. DTO fiel aos campos reais

Módulo proposto `vet_tech/features/clinical/consultation_pdf.py` para DTO/normalização; template/renderizador propostos `consultation_pdf_template.py` no mesmo domínio. Integração permanece no ClinicalMixin e cliente compartilhado. Não criar árvore paralela services/ nem mover módulos atuais.

| Seção do DTO | Origem confirmada | Regra de apresentação |
|---|---|---|
| Consulta | id, pet_id, veterinario_id, status, motivo, diagnostico, obs, data_atendimento/data, agendada_para, iniciada_em, finalizada_em, retorno_previsto | Campos publicados apenas; datas civis e instantes formatados pelos helpers. Não fabricar anamnese/conduta como campos diferentes. |
| Pet | id e nome de assert_owner | Sem endereço/CPF/telefone do tutor ou foto remota. |
| Autoria | veterinario_id da consulta | Exibir ID do responsável; nome/CRMV/assinatura não vêm garantidos e não serão buscados em endpoint de conta alheia. |
| Vacinas | vacina, lote, data_aplicacao, data_prox_dose | Diferenciar aplicação e próxima dose prevista. |
| Medicamentos | nome, dose, unidade, dosagem, frequencia, via, tipo, data_inicio, data_fim | Preservar dose/unidade; dosagem apenas como fallback legado já existente, sem inferir unidade. Término ausente pode ser contínuo conforme tipo, sem inventar fim. |
| Diagnósticos pontuais | diagnosticos: nome, doenca_id, data_diagnostico, estado, observacoes, publicado_em | Usar só vínculo desta consulta. Não imprimir doencas consolidadas como diagnóstico. |
| Exames | tipo, status, data_solicitacao, data_realizacao/data, resultado | Somente vinculados; solicitado não implica realizado. Sem anexos/URLs carregadas. |

Todos os complementos devem conferir pet_id e consulta_id, mesmo após filtragem no Xano. Ausentes: omitir seção vazia ou mostrar `Não informado` em campo de identificação; zero numérico não vira ausência. Rejeitar resposta inconsistente em vez de encaixar dados no relatório errado. Ordenação determinística por data disponível e ID, sem alterar cronologia clínica ou agrupar dados de consulta distinta.

### 5. Renderizador e modelo visual

Escolha planejada: **ReportLab/Platypus** como único motor PDF, com template Python versionado e texto escapado antes de Paragraph. Não adicionar Jinja2/WeasyPrint simultaneamente. É uma alternativa à sugestão HTML do brief, justificada pela ausência de contrato de deploy que garanta Pango e pela necessidade de evitar dependência gráfica de sistema não confirmada. Não se afirma que ReportLab esteja instalado ou homologado: um teste de compatibilidade no runtime de destino é checkpoint obrigatório antes da instalação definitiva e da integração funcional.

[WeasyPrint exige Pango e dependências de sistema](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html); [ReportLab oferece fontes TrueType Unicode](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/) e [Platypus para documentos paginados](https://docs.reportlab.com/reportlab/userguide/ch5_platypus/). São fontes oficiais consultadas em 04/11/2026. Selecionar/fixar versão compatível em requirements após a prova no Python de destino; não escolher versão por memória.

A4, margens de 18 mm, verde derivado dos tokens reais, cabeçalho VetTech, identificação, seções clínicas e rodapé com número de página. Asset local candidato mascote_logo.png, sujeito à aprovação do modelo visual antes de congelar o template. Usar fonte Unicode empacotada e licenciada com o motor ou asset licenciado local; não depender da fonte web nem de fontes presentes no computador do usuário. Validar licença e distribuição. Textos e tabelas precisam quebrar em múltiplas páginas, incluindo parágrafo/linha maior que uma página, sem truncar. Nenhuma imagem clínica ou URL remota será resolvida pelo renderizador; assets em allowlist local fixa. Sem assinatura ou campos de clínica não comprovados.

### 6. Evento, concorrência e isolamento

Evento no ClinicalMixin captura sessão/geração/token/perfil/pet/detail_id e um identificador da operação; guarda loading e chave de retry como estado privado necessário, sem bytes/payload de PDF serializados. Alterar pet/consulta, sair do detalhe ou logout invalida a geração da exportação, inclusive voltar ao mesmo ID antes da resposta. Usar evento em background seguindo o padrão fetch_tutor_clinical, com locks curtos e renderização fora do event loop; caso contrário a troca de pet pode ficar bloqueada atrás da exportação.

Fazer a chamada autorizada com xano_request; validar envelope e auditoria_id antes de renderizar. Renderizar em tarefa/thread controlada e bytes locais, sem arquivo temporário público. Revalidar contexto depois do HTTP, depois da renderização e imediatamente antes de emitir rx.download. Uma operação ativa por sessão e limite de renderizações concorrentes por worker impedem mistura/exaustão; configurar limite de bytes/tempo a partir da prova de deploy e falhar com mensagem segura, sem entregar PDF truncado. Não usar cache global de dados/pdfs nem fila persistente nova.

Limpar loading apenas se o identificador ainda corresponde à operação corrente: finally de uma solicitação velha não pode liberar o botão de outra. Timeout/429 com resposta incerta conserva chave para retry do mesmo alvo; erro de renderização permite retry da mesma emissão autorizada. Depois de sucesso, limpar chave; novo pedido é nova emissão auditada. A UI continua mostrando a consulta e permite retorno ao fluxo existente.

## Risks / Trade-offs

- A API remota pode divergir dos .xs → validar grupos, contratos, autorização e índices no ambiente de desenvolvimento antes de código funcional/publicação; não usar credencial pessoal ou produção implicitamente.
- Tabela exige veterinario_id enquanto ator é tutor → preencher responsável da consulta e tutor_id como ator; testar auditoria_GET e semântica de exibição sem atribuir clique ao profissional.
- Conflito concorrente de índice único no Xano → teste remoto com mesma chave e retry; não aceitar um check-then-insert sem garantia de unicidade/tratamento transacional.
- Documento simples em Platypus dá menos reaproveitamento de CSS → template isolado, modelo aprovado e prova de layout longo; mudar de motor requer revisão do design antes da aplicação.
- Base64 e geração em memória ampliam consumo → teste no deploy, limite de payload e concorrência, sem fallback silencioso para URL pública.
- Dados clínicos em falhas ou fontes externas → sanitização de mensagens, logs sem payload, texto escapado e allowlist de assets.

## Migration Plan

1. Confirmar ambiente Xano de desenvolvimento autorizado, contratos publicados e disponibilidade de runtime; registrar apenas evidências sanitizadas. Nenhum workspace remoto foi consultado neste planejamento; não há ferramenta Xano conectada nesta sessão. Isso não prova ausência de credenciais locais, que não foram lidas ou copiadas.
2. Validar motor, fonte/licença, tamanho/memória/tempo e aprovar modelo visual com dados sintéticos. Sem manifesto de hospedagem, não afirmar suporte nativo nem instalar dependência definitivamente antes desse checkpoint.
3. Implementar/publish operação Xano proposta com testes de proprietário, publicação, auditoria, idempotência e falhas; sem nova tabela. Confirmar endpoint remoto antes de habilitar o botão funcional.
4. Implementar DTO, template, evento e UI; executar testes unitários e navegador e smoke remoto de desenvolvimento. Documentar configuração/limites em `docs/consulta-pdf.md` e comandos em ambiente seguro.
5. Liberar aplicação somente com contrato remoto e testes confirmados. Rollback: retirar/desabilitar ação de exportação na aplicação e despublicar a nova operação se necessário, mantendo logs imutáveis, dados clínicos e demais leituras; não remover históricos nem tabelas.

### Checkpoints que condicionam a implementação

A proposta está pronta para revisão, mas não significa que ambiente remoto/deploy ou marca estejam homologados. Antes de implementação funcional: obter acesso autorizado ao ambiente de desenvolvimento e verificar contrato; registrar runtime de hospedagem e prova do motor escolhido; apresentar layout sintético e confirmar o asset oficial. Esses são entregáveis específicos das tarefas iniciais. Se algum checkpoint exigir mudar o motor, esquema de dados ou escopo por perfil, revisar os artefatos antes de continuar, sem inventar contrato publicado.

## Decisões confirmadas durante aplicação

O usuário confirmou execução apenas local. A prova inicial foi executada no Linux/Python 3.13.5 com ReportLab 5.1.0. Limites e comparação do Xano remoto estão em verification.md. Não há homologação de hospedagem externa implícita. O modelo inicial foi substituído pela referência oficial fornecida pelo usuário, documentada na seção seguinte.

No teste remoto, `error_type=conflict` foi recusado pelo runtime Xano. A implementação usa `inputerror` (HTTP 400) para estado inelegível e chave conflitante, preservando as negativas e mensagens de domínio; a aplicação tratará tanto 400 quanto 409 se recebido. Não houve alteração de regra de acesso.

## Modelo visual oficial recebido

O usuário forneceu o relatório de referência e confirmou seu uso como modelo oficial na continuação. O arquivo encontrado em docs/VetTech — relatório clínico pronto para orientar a implementação.pdf foi preservado e copiado para o caminho solicitado docs/templates/vettech-prontuario-referencia.pdf (SHA-256 acf5b3f7c4e24468024a21a5074aa22123b5093def82f0f802b9c03a3624e6e7). A referência possui cinco páginas demonstrativas; a saída terá uma capa e quantas páginas dinâmicas o conteúdo exigir. Elementos: verde #315f3e, corpo sans serif Unicode, capa com tartaruga V e marca d’água, identificação tabular, tabelas, cabeçalho com mascote e rodapé numerado. Foram extraídas somente as duas imagens individuais com transparência para assets/consultation-pdf, sem rasterizar página ou carregar o PDF no runtime. Textos/dados fictícios da referência não integram o template. A fonte local Bitstream Vera aproxima a sans serif e preserva PT-BR; fontes comerciais da referência não foram distribuídas.

### Ajuste de espaçamento da marca d’água

Conforme pedido após inspeção do PDF, o texto VetTech da marca d’água nas páginas internas foi deslocado 8 mm para baixo. A tartaruga e todos os demais elementos, incluindo capa, cabeçalho, rodapé, tabelas e conteúdo, mantêm suas posições.
