# VetTech — Brief técnico para OpenSpec: exportação de consulta em PDF

> **Status:** proposta de change; ainda não implementada.
> **Change ID sugerido:** `exportar-consulta-pdf`
> **Repositório-alvo informado:** `sabortech/vet-tech`
> **Pilha informada:** Reflex (Python), Xano (API/backend).
> **Revisão de 04/11/2026:** repositório `sabortech/vet-tech`, branch `main`, árvore Git SHA `6750cefce8aad7cd79a05782f835be47f0f2a8e6` consultada via GitHub. Foram inspecionados componentes, State, cliente Xano, XanoScript e specs. O workspace Xano remoto autenticado não foi consultado diretamente: o contrato abaixo é confirmado pelo código versionado, mas publicação/sincronização remota precisam de verificação pelo Codex.

## 0. Evidências concretas da revisão do repositório

**Fonte:** [`sabortech/vet-tech`](https://github.com/sabortech/vet-tech), `main`, árvore Git `6750cefce8aad7cd79a05782f835be47f0f2a8e6`. Não confundir código XanoScript versionado com verificação de endpoints publicados no workspace Xano.

| Área | Evidência confirmada | Consequência para a change |
|---|---|---|
| Stack | `requirements.txt`: `reflex==0.9.11`, `python-dotenv>=1.0,<2`, `tzdata>=2025.2`; `xano_client.py` importa `httpx` | `WeasyPrint`, `Jinja2`, `ReportLab` não constam das dependências diretas; checar resolução transitiva e suporte real de deploy antes de escolher. |
| Composição da sessão | `vet_tech/features/auth/state.py`: `State(SupportChatMixin, TutorDashboardMixin, ClinicalMixin, rx.State)` | Não criar um segundo State de autenticação. Adicionar evento ao `ClinicalMixin` ou serviço associado. |
| Tela exata | `vet_tech/components/clinical.py`: `consultation_detail()` e `tutor_consultations()` | Adicionar o botão ao detalhe do prontuário do **tutor**, sem inventar rota nova. |
| Seleção de consulta | `vet_tech/features/clinical/state.py`: `show_consultation_detail(value)` define `detail_id`, `detail` e `detail_sections` a partir de `history_rows` | Há contexto já carregado, mas ele é apresentação/cache e **não substitui** validação autorizada do backend na exportação. |
| Leitura tutor | `fetch_tutor_clinical()` chama `GET tutor/pets/{pet_id}/historico` e `GET tutor/consultas?pet_id=...` via `xano_request` | Usar o mesmo cliente e os mesmos contratos; não supor `GET /consultas/{id}`. |
| Grupo Xano | `vet_tech/features/clinical/state.py`: `GROUP = "vettech-clinical"`; `xano_client.py` monta `{base}/api:{group}/{endpoint}` | Reutilizar `xano_request` e `XANO_API_BASE_URL`, token de sessão e eventual `X-Tenant`. |
| Autorização | `xano/api/clinical/tutor_history_GET.xs` chama `Clinical/assert_owner` | Tutor só exporta histórico do próprio pet. A operação deve revalidar acesso no momento da exportação. |
| Contrato de consulta | `xano/api/clinical/tutor_consultations_GET.xs` retorna lista filtrada por pet, com conteúdo clínico apenas para `finalizada` ou legado sem status | Não exportar agendamentos ou rascunhos. Não confiar em ID ou status enviados pelo navegador. |
| Conteúdo publicado | `xano/function/clinical/history.xs` agrega `consultas`, `vacinas`, `medicamentos`, `exames`, `diagnosticos`, `doencas` | Filtrar por `consulta_id` **após** resposta autorizada, reproduzindo a associação da UI; definir política para registros legados sem vínculo. |
| Auditoria | `xano/function/clinical/audit.xs` grava `log_acesso`; `openspec/specs/record-access-control/spec.md` exige auditar exportações | O endpoint de leitura atual não prova auditoria específica de **exportar**. É uma lacuna funcional obrigatória, não opcional. |
| Identidade visual | `assets/vet_tech.css`, `assets/mascote_logo.png`, `assets/favicon.svg`, `assets/mascote/` | Derivar layout de marca real; validar com a equipe qual logotipo/modelo é o oficial do documento. |
| OpenSpec | `openspec/config.yaml`, `openspec/specs/clinical-records/spec.md`, `openspec/specs/record-access-control/spec.md`, `.agents/skills/openspec-propose/SKILL.md` | Propor change incremental, respeitando regras existentes de autorização, auditoria e português. |
| Testes | `tests/unit/test_clinical_state.py`, `test_xano_client_clinical.py`, `tests/integration/consultations_browser.py`, `scripts/clinical_smoke.py` | Adicionar testes adjacentes, não criar infraestrutura de testes paralela. |

**Importante — escopo por perfil:** a tela de detalhe encontrada é do **tutor**. A área do veterinário usa fluxo próprio de atendimento em `vet_tech/pages/atendimento.py` / `vet_tech/components/clinical.py`. Para evitar lacuna de produto, a change deve declarar se a V1 é **exportação pelo tutor apenas** (padrão recomendado para esta entrega) ou também pelo veterinário. Se incluir veterinário, exigir autorização ativa e auditoria específica em Xano, sem reutilizar cegamente o fluxo do tutor.

## 1. Objetivo e resultado esperado

Adicionar na tela de detalhes de uma consulta veterinária um botão **Exportar PDF**, capaz de gerar e baixar um documento A4 com a identidade visual oficial do VetTech e os dados da consulta existente. Reutilizar a integração atual com Xano e, preferencialmente, o endpoint já utilizado para consultar o registro por ID. Não criar banco adicional. **Exceção obrigatória a decidir no design:** um endpoint/ação Xano dedicado de exportação ou auditoria pode ser necessário para registrar `exportar_consulta` de forma confiável e revalidar a permissão imediatamente antes de entregar dados sensíveis. Não dispensar a auditoria exigida pelas specs atuais apenas para evitar endpoint novo.

### Experiência do usuário

1. Usuário autenticado e autorizado acessa os detalhes de uma consulta.
2. Clica em **Exportar PDF**; o botão mostra estado de processamento e evita cliques duplicados.
3. O backend Python do Reflex consulta ou reutiliza de modo seguro os dados do endpoint Xano existente, usando o ID real e o mecanismo de autenticação atual.
4. Um serviço de PDF renderiza esses dados em um template versionado do VetTech.
5. O navegador baixa `vettech-consulta-<id>.pdf` (nome sanitizado).
6. Em caso de erro, a interface apresenta mensagem compreensível, sem expor dados pessoais, stack traces ou credenciais.

## 2. Descoberta obrigatória antes da implementação

**Não começar a escrever código até registrar em `proposal.md`/`design.md` as evidências abaixo, referenciando arquivos, funções e linhas quando possível.**

### 2.1 Inspeção do projeto Reflex (itens já localizados; validar no checkout atual)

- Ler `README`, `pyproject.toml`, `requirements*.txt`, `.python-version`, `rxconfig.py` e configuração de deploy, se existirem.
- Identificar versões reais de Python/Reflex, estrutura de pastas, componentes compartilhados, tema, logotipo e arquivos de identidade visual.
- Localizar a rota/tela de detalhe da consulta, seu State e o evento que carrega o registro; distinguir componentes de renderização dos eventos executados no servidor.
- Mapear utilitários HTTP existentes (`httpx`, `requests` etc.), headers, tokens/sessão e tratamento de erros. Não copiar autenticação para um segundo cliente.
- Verificar se já existem exportações, geração de PDF, Jinja2, CSS de impressão, testes e mecanismos de arquivos/download.
- Verificar se `rx.download` na versão instalada aceita dados em memória (bytes/base64/data URI, conforme API efetivamente instalada) e qual forma é adequada para o tamanho do arquivo. Não presumir assinatura da função.
- Revisar restrições de execução no ambiente de hospedagem (binários, bibliotecas do SO, filesystem efêmero, workers, tamanho máximo e memória).

### 2.2 Auditoria das APIs Xano (contratos versionados localizados; validar publicação remota)

- Localizar **o endpoint real** da consulta por ID e seus usos no projeto. Documentar método, URL relativa, parâmetros, autorização, status HTTP, exemplos seguros e formato de resposta.
- Verificar se a resposta contém todos os dados necessários, inclusive possíveis objetos relacionados de paciente/animal, tutor, veterinário, histórico/anamnese, diagnóstico, conduta, prescrição, data/hora e identificação da clínica. Não presumir que todos esses campos existem.
- Identificar eventual paginação, arrays aninhados, respostas vazias, campos opcionais e dados sensíveis.
- Confirmar se o endpoint já garante autorização por usuário/clínica e se o backend Reflex precisa reforçar o controle de acesso. Não aceitar ID arbitrário sem validação/autorização.
- Se algum dado não vier na consulta, verificar se já há endpoint relacionado que possa ser reutilizado; **não modificar Xano inicialmente**.
- Para acesso direto à plataforma Xano, usar apenas documentação, export/OpenAPI ou credenciais/integrações autorizadas e disponíveis. Nunca solicitar ou registrar tokens em texto claro nos arquivos OpenSpec.
- Se o projeto não contiver contrato/fixture nem houver acesso à API autenticada, declarar o bloqueio e registrar campos pendentes; **não criar um payload fictício como se fosse real**.

### 2.3 Auditoria OpenSpec

- Inspecionar `openspec/config.yaml`, `openspec/specs/`, `openspec/changes/`, `AGENTS.md` e instruções do repositório.
- Detectar a versão e o workflow OpenSpec efetivamente instalado. Não assumir estrutura de diretórios ou comandos desatualizados.
- Consultar as specs existentes para propor uma alteração incremental sem conflitar com outras changes.

## 3. Decisões arquiteturais propostas

### 3.1 Fluxo de dados

```text
Tela de detalhes (Reflex)
    └── clique em Exportar PDF
         └── evento no State (servidor)
              ├── valida sessão e acesso à consulta
              ├── obtém consulta via cliente Xano existente
              ├── normaliza resposta em DTO próprio para documento
              ├── renderiza template com autoescape
              ├── converte HTML em PDF
              └── dispara download através da API compatível do Reflex
```

**Separar responsabilidades:** integração Xano, mapeamento/normalização, template visual, geração PDF e evento de interface. Reusar módulos existentes em vez de criar uma árvore paralela de `services/` sem necessidade.

### 3.2 Templates e identidade visual

- Criar um template **oficial do VetTech**, versionado, com marca/logotipo, cabeçalho, detalhes de consulta, seções clínicas presentes no payload, assinatura/identificação profissional apenas se a informação existir, data e rodapé.
- Priorizar assets e variáveis visuais que **já existem** no repositório; não inventar logotipo, endereço, CRMV, assinatura, clínica ou identificação profissional.
- Se a equipe disponibilizar um modelo de relatório (PDF/Word/imagem), reproduzir esse modelo com fidelidade; se não, criar layout inicial simples baseado no tema real, deixando o design passível de troca sem alterar lógica.
- Layout A4 com margens consistentes, paginação, quebra de página correta, campos longos, acentuação Unicode e listas/tabelas quando necessário.
- Sem inserir HTML de campos do usuário como markup: escapar conteúdo e restringir URLs de imagens/assets.
- Para valores ausentes, seguir regras explícitas: ocultar seção opcional ou exibir marcador padronizado; nunca inventar diagnóstico, prescrição ou assinatura.

### 3.3 Escolha de biblioteca

**Opção a avaliar (não instalada):** `Jinja2` para template HTML/CSS + `WeasyPrint` para conversão PDF, pela facilidade de preservar o modelo visual próprio do VetTech. **Decisão condicionada à auditoria** de dependências, compatibilidade Python/Windows/Linux e infraestrutura de deploy.

Caso o WeasyPrint exija dependências nativas incompatíveis ou inviáveis no ambiente do projeto, avaliar `ReportLab` como alternativa Python para PDF, registrando justificativa no `design.md`. Evitar adicionar as duas bibliotecas sem necessidade. Reutilizar dependências já instaladas quando atenderem aos requisitos.

### 3.3.1 Decisão pendente prioritária: auditoria de exportação

O README (RF08) e `openspec/specs/record-access-control/spec.md` exigem log de exportação. `GET tutor/pets/{pet_id}/historico` valida proprietário, mas não contém chamada explícita a `Clinical/audit`; `GET veterinario/pets/{pet_id}/historico` registra **visualizar_historico**, não **exportar**. Portanto, a change NÃO DEVE afirmar que a exportação está auditada por simplesmente chamar a leitura existente.

O Codex deverá projetar uma operação Xano autenticada de exportação/registro com autorização por perfil/pet/consulta, auditabilidade e sem exposição de rascunhos; preferir operação que valide e audite no mesmo fluxo transacional antes de devolver os dados. Para o tutor, revisar `Clinical/audit` que já aceita `tutor_id` e `consulta_id`; para veterinário, `Clinical/assert_access` com consentimento ativo. Não enviar dados sensíveis a endpoint de auditoria sem controle de acesso. Falha na auditoria deve impedir exportação bem-sucedida. Especificar idempotência para evitar logs duplicados em retries e política para tentativa negada. A API remota publicada e permissões precisam ser verificadas antes de executar a implementação.

### 3.4 Persistência

- **V1 sem persistir PDFs:** gerar sob demanda em memória no processo servidor, sem nova tabela Xano ou armazenamento externo.
- A fonte de verdade permanece sendo o registro da consulta no Xano.
- Registrar como evolução futura, fora do escopo, a preservação imutável de documentos emitidos/assinados caso exigências operacionais ou regulatórias tornem isso necessário.

### 3.5 Segurança e privacidade

- Somente usuário autenticado e autorizado pode exportar o registro.
- Consultar Xano pelo mesmo fluxo confiável do detalhe, sem expor tokens de Xano, API keys ou payloads sensíveis em logs.
- Não armazenar cópias temporárias em pastas públicas nem disponibilizar links previsíveis para documentos clínicos.
- Minimizar campos de dados pessoais, sanitizar nome do arquivo, tratar entrada HTML com autoescape e impedir chamadas a recursos externos não confiáveis durante geração.
- Não afirmar conformidade legal automática; revisar políticas aplicáveis de tratamento de dados conforme contexto real do sistema.

## 4. Contrato interno do gerador (a definir com dados reais)

Criar um DTO/objeto normalizado que a camada PDF consome, independente do formato bruto da API. **Mapeamento de campos obrigatoriamente derivado do contrato Xano encontrado**, por exemplo:

| Seção possível | Origem a identificar | Regra |
|---|---|---|
| Identificação da consulta | ID, data, status | Exibir apenas campos existentes |
| Animal/paciente | Relação com cadastro animal | Não assumir formato/nome do campo |
| Tutor | Relação com cliente/tutor | Exibir mínimo necessário |
| Veterinário | Relação com usuário/profissional | Não inventar CRMV |
| Anamnese | Campos clínicos da consulta | Preservar quebras de linha |
| Diagnóstico/conduta | Campos efetivamente existentes | Se ausente, não inventar |
| Prescrição/orientações | Campos ou entidades relacionadas | Respeitar ordem e itens existentes |
| Identidade visual | Assets do projeto | Sem novos dados de clínica não confirmados |

**Nota:** a tabela é uma checklist de investigação, **não é o schema real da API**.

## 5. Requisitos funcionais — para a spec OpenSpec

### RF-01: botão de exportação
Na tela de detalhes da consulta, o sistema **DEVE** exibir o botão `Exportar PDF` quando o usuário tiver permissão e um ID de consulta válido.

### RF-02: dados reais da consulta
A exportação **DEVE** usar o endpoint Xano já presente no projeto e o ID da consulta aberta; **NÃO DEVE** produzir dados de demonstração em produção.

### RF-03: documento padronizado
O PDF **DEVE** respeitar o template visual VetTech, com campos mapeados do JSON real, e suportar português brasileiro, acentuação e conteúdo longo com múltiplas páginas.

### RF-04: download
O sistema **DEVE** permitir baixar um PDF válido com MIME `application/pdf`, nome previsível e seguro, mantendo o usuário na tela da consulta.

### RF-05: estados e falhas
A interface **DEVE** mostrar carregamento e feedback para falha de autenticação, autorização negada, registro inexistente, indisponibilidade Xano e erro de renderização, sem vazamento de informação sensível.

### RF-06: sem armazenamento adicional
A V1 **NÃO DEVE** criar banco, tabela ou persistência de PDF; **DEVE** usar a tabela de auditoria já existente, admitindo endpoint Xano novo para registrar exportação com segurança.

### RF-07: compatibilidade
A implementação **DEVE** funcionar com as versões de Python, Reflex e deploy identificadas no repositório.

## 6. Cenários de aceitação (Given / When / Then)

1. **Consulta válida** — Dado um usuário autorizado numa consulta existente, quando clicar em Exportar PDF, então recebe arquivo PDF correspondente ao ID atual, com identidade VetTech e campos realmente retornados pela API.
2. **Sem permissão** — Dado usuário não autorizado, quando tentar exportar consulta de terceiros (inclusive alterando ID), então recebe negativa e nenhum documento é gerado ou exposto.
3. **Registro inexistente** — Dado ID inexistente, quando tentar exportar, então vê mensagem de erro apropriada e nenhum documento parcial é baixado.
4. **Campos opcionais ausentes** — Dada consulta sem algum campo opcional, quando exportar, então o PDF é válido e não exibe valores fabricados nem `None`/`undefined`.
5. **Texto longo** — Dada consulta com anamnese/conduta longa, quando exportar, então texto não é truncado e páginas seguem layout legível.
6. **Acentuação** — Dado conteúdo com `ç`, `ã`, `é` e caracteres usuais, então o PDF preserva a renderização.
7. **Falha Xano** — Dada falha de rede ou HTTP 5xx, quando exportar, então o estado de loading termina e o usuário recebe feedback sem dados sensíveis.
8. **Falha de geração** — Dado erro de template/conversão, então não há download corrompido e o erro é tratado.
9. **Concorrência** — Quando o usuário clica repetidamente ou outros usuários geram simultaneamente, então os arquivos não se misturam e o estado não fica preso.
10. **Regressão** — A consulta na tela e os demais fluxos atuais continuam funcionando após a feature.

## 7. Escopo / fora do escopo

**Dentro:** auditoria, ajuste mínimo de dependências, gerador isolado, template, download via Reflex, testes, documentação breve e change OpenSpec.

**Fora:** criação de banco novo, alterações de domínio Xano, geração em lote, envio por e-mail/WhatsApp, assinatura eletrônica/digital, storage permanente, links públicos, edição do PDF e sistema de versionamento de relatórios.

## 8. Entregáveis exigidos do Codex

1. Análise factual dos arquivos do projeto e do fluxo de consulta/Xano no `design.md`, incluindo riscos e dependências; explicitar o que não foi possível confirmar.
2. **Change OpenSpec** de nome `exportar-consulta-pdf`, respeitando os comandos e formato presentes no projeto, com `proposal.md`, `design.md`, `tasks.md` e specs delta da(s) capacidade(s) afetada(s), conforme a versão instalada.
3. Especificação com requisitos normativos e cenários verificáveis, incluindo casos de erro e autorização.
4. Plano de tarefas pequeno e ordenado, com testes e checkpoints; não modificar implementação antes de validar a proposta/change.
5. Se solicitado posteriormente, implementação e testes automatizados respeitando a arquitetura encontrada.

### Estrutura indicativa, caso a versão OpenSpec aceite o formato

```text
openspec/changes/exportar-consulta-pdf/
├── proposal.md
├── design.md
├── tasks.md
└── specs/
    └── exportacao-consulta-pdf/
        └── spec.md
```

A estrutura é **ilustrativa**. O Codex deve usar a estrutura e convenções reais definidas pelo OpenSpec instalado e por `openspec/config.yaml`.

## 9. Plano sugerido de implementação após aprovação da change

- [ ] Mapear a rota e o State do detalhe da consulta.
- [ ] Inspecionar cliente Xano e confirmar endpoint/resposta/autorização.
- [ ] Identificar assets e modelo visual do VetTech.
- [ ] Validar biblioteca PDF e dependências no deploy.
- [ ] Construir mapeador de dados com validações e campos opcionais.
- [ ] Criar template padronizado e serviço de PDF isolado/testável.
- [ ] Adicionar evento Reflex e botão com loading/feedback.
- [ ] Cobrir cenários críticos com testes (mock Xano e saída PDF).
- [ ] Validar manualmente download e layout A4 com consulta representativa, em ambiente seguro.
- [ ] Atualizar documentação sem publicar dados clínicos, tokens ou exemplos sensíveis.

## 10. Prompt pronto para colar no Codex

> Leia `vettech-exportar-consulta-pdf-openspec.md` integralmente. **Sua tarefa agora é criar somente uma change OpenSpec**, chamada `exportar-consulta-pdf`, e não implementar a funcionalidade. Antes de redigir a change, faça uma auditoria real deste repositório: estrutura Reflex, fluxo/tela/State de consulta, cliente Xano, endpoint de consulta usado atualmente, autenticação, resposta JSON, assets de identidade visual, dependências e ambiente de deploy. Inspecione `openspec/`, `AGENTS.md` e as instruções locais para seguir o workflow da versão OpenSpec instalada. Documente em `design.md` as evidências concretas (arquivos/funções) e o que estiver indisponível. **Não invente endpoints, campos, logos ou credenciais.** Proponha HTML/CSS + Jinja2 + WeasyPrint apenas se compatível com o deploy; caso contrário, justifique alternativa (por exemplo ReportLab). O PDF deve usar o modelo oficial do VetTech e dados reais dos endpoints versionados `tutor/pets/{pet_id}/historico` e `tutor/consultas?pet_id=...`, ser gerado sob demanda e baixado via Reflex sem criar armazenamento adicional. Planeje obrigatoriamente a auditoria de `exportar_consulta` no Xano, com revalidação de autorização e falha fechada, pois a leitura atual não registra exportação. Crie proposal, design, tasks e specs delta com requisitos, cenários de erro e testes, sem alterar ainda o código da aplicação. Ao terminar, liste os arquivos OpenSpec criados, decisões técnicas tomadas, contratos de API verificados e pendências antes da implementação.

## 11. Critérios de qualidade para a change

- Nenhuma rota, campo ou nome de arquivo fictício tratado como existente.
- A fonte dos dados é o Xano existente; o documento PDF não é fonte de verdade.
- Autorização testada e definida para exportação por ID.
- Template substituível sem alterar o fluxo de integração.
- Separação entre apresentação, coleta/mapeamento e renderização PDF.
- Compatibilidade de runtime/deploy considerada antes de fixar a biblioteca.
- Proposta revisável antes de qualquer alteração funcional.


## 12. Contratos reais do Xano e mapeamento para o template

### 12.1 Rotas versionadas (não afirmar que estão publicadas sem teste remoto)

- `GET /api:vettech-clinical/tutor/pets/{pet_id}/historico` — `xano/api/clinical/tutor_history_GET.xs`, autenticação `tutor`, chama `Clinical/assert_owner` e `Clinical/history`. Retorna objeto com listas `consultas`, `vacinas`, `medicamentos`, `exames`, `diagnosticos`, `doencas`.
- `GET /api:vettech-clinical/tutor/consultas?pet_id={pet_id}` — `xano/api/clinical/tutor_consultations_GET.xs`, autenticação `tutor`, retorna lista com consulta `finalizada` ou legado; para outros estados retorna somente campos mínimos.
- `GET /api:vettech-clinical/veterinario/pets/{pet_id}/historico` — `xano/api/clinical/vet_history_GET.xs`, autenticação `veterinario`, `Clinical/assert_access` e auditoria de **visualização**. Fora do escopo inicial do botão tutor.
- `GET /api:vettech-clinical/tutor/pets/{pet_id}/auditoria` — `xano/api/clinical/audit_GET.xs`, lista `log_acesso` ao tutor proprietário; **não grava** exportação.

### 12.2 Campos versionados, sem dados fictícios

`consulta`: `id`, `pet_id`, `veterinario_id`, `status`, `agendada_para`, `iniciada_em`, `finalizada_em`, `motivo`, `data_atendimento`, `data`, `diagnostico`, `obs`, `retorno_previsto`, `versao`.

Complementos com `consulta_id`:
- `vacinas`: `vacina`, `lote`, `data_aplicacao`, `data_prox_dose`, `veterinario_id`.
- `medicamentos`: `nome`, `dosagem`, `dose`, `unidade`, `frequencia`, `via`, `tipo`, `data_inicio`, `data_fim`.
- `exames`: `tipo`, `status`, `data_solicitacao`, `data_realizacao`, `resultado`.
- `diagnosticos`: `doenca_id`, `nome` (enriquecido por catálogo), `data_diagnostico`, `estado`, `observacoes`, `publicado_em`.
- `doencas`: inclui condição consolidada e legados; **não imprimir indiscriminadamente** como se fossem diagnósticos daquela consulta.

O retorno `Clinical/history` exclui consultas não publicadas e seus complementos vinculados; há registros legados sem `consulta_id`. A V1 deve documentar se os exclui do PDF de **consulta específica** (recomendado), evitando atribuição clínica incorreta. Identificação do pet e nome do veterinário **não estão garantidos** pelo payload de histórico: verificar o cadastro do pet e perfil profissional autorizado, ou apresentar apenas IDs quando adequado; nunca criar nomes, CRMV ou assinatura.

### 12.3 Mapeamento fiel à UI existente

A função `show_consultation_detail` seleciona a consulta pelo ID em `history_rows["consultas"]` e filtra complementos pelo `consulta_id`; o botão deve ficar em `consultation_detail()` de `vet_tech/components/clinical.py`, junto a `Voltar à lista`. Revalidar `selected_pet_id`, `detail_id`, sessão, geração e retorno Xano antes do PDF, impedindo vazamento por resposta atrasada após troca de pet/logout. A função `cards()` em `vet_tech/features/clinical/state.py` transforma valores para strings e adiciona rótulos de data: o PDF deve preferir dados brutos autorizados e formatar com `vet_tech/shared/dates.py` em vez de depender de textos da tela.

### 12.4 Requisitos adicionais da change

- **RF-08 — Autorização e auditoria:** toda exportação bem-sucedida DEVE validar o tutor proprietário (ou veterinário autorizado se habilitado), registrar `exportar_consulta` com pet, consulta, ator e timestamp e negar o download se a auditoria falhar.
- **RF-09 — Somente publicado:** consulta `agendada` ou `em_atendimento` e rascunhos não podem aparecer em PDF. Consulta `legado` deve seguir política explícita de publicação.
- **RF-10 — Isolamento de sessão:** pet/consulta trocados, logout e resposta assíncrona atrasada não podem entregar PDF de contexto anterior.
- **RF-11 — Dados vinculados:** somente complementos cuja `consulta_id` corresponda à consulta selecionada, sem confundir condição consolidada com diagnóstico pontual.
- **RF-12 — Layout real:** logo oficial validado; A4, quebra de páginas, fontes compatíveis, campos vazios e ausência de CRMV/assinatura tratados sem fabricação.

### 12.5 Testes que não podem faltar

- Tutor exporta consulta finalizada própria; documento começa com assinatura `%PDF-` e inclui campos correspondentes ao payload versionado.
- Tutor tenta consulta de outro pet/ID forjado; nenhum PDF nem registro de exportação bem-sucedida.
- Exportação após logout/troca de pet enquanto request está pendente; nenhum download indevido.
- Consulta agendada/em atendimento e complementos não publicados; bloqueio.
- Auditoria Xano falha; nenhum download é disponibilizado. Verificar registro de `exportar_consulta` na trilha auditável.
- Consulta com vacinas, medicamentos, diagnósticos e exames; filtro estrito por `consulta_id`.
- Legado sem `consulta_id`; não associar arbitrariamente ao relatório.
- Conteúdo longo, quebras de página, caracteres PT-BR, sanitização e renderização sem recursos externos.
- Regressão dos testes existentes de `ClinicalMixin`, cliente Xano, consultas e permissões.

### 12.6 Pontos que continuam exigindo validação real

1. **Workspace Xano remoto:** comparar rotas, grupos, contratos e regras de autorização publicados com os `.xs` versionados; não assumir deploy sincronizado.
2. **Modelo visual oficial do PDF:** há assets de marca, mas nenhum modelo de relatório foi fornecido; solicitar/confirmar design antes de congelar template.
3. **Hospedagem:** verificar suporte real a bibliotecas nativas e mecanismo de `rx.download` no Reflex 0.9.11.
4. **Autorização de exportação:** definir e implementar ação Xano segura que produza auditoria específica; não substituir por log no frontend.
5. **Perfil alvo:** esta proposta é tutor no detalhe existente; veterinário é extensão separada salvo decisão explícita.

## 13. Prompt Codex revisado (usar este no lugar do prompt da seção 10)

> No checkout de `sabortech/vet-tech`, leia integralmente `vettech-exportar-consulta-pdf-openspec.md`, `AGENTS.md`, `docs/architecture.md`, `openspec/config.yaml`, as specs `clinical-records` e `record-access-control` e a skill local `openspec-propose`. Crie **somente** a change OpenSpec `exportar-consulta-pdf` (sem implementar, sem commit). Reaproveite a tela `vet_tech/components/clinical.py::consultation_detail`, o `ClinicalMixin` e `xano_request`. Os contratos versionados são `tutor/pets/{pet_id}/historico` e `tutor/consultas?pet_id=...`, com `Clinical/history` retornando `consultas`, `vacinas`, `medicamentos`, `exames`, `diagnosticos` e `doencas`. A V1 exporta **uma consulta finalizada do tutor** e complementos com `consulta_id` correspondente; não exporta rascunhos. A especificação DEVE planejar revalidação de proprietário e auditoria específica `exportar_consulta` em Xano antes de entregar PDF, pois o endpoint atual não audita exportação. Avalie compatibilidade Reflex 0.9.11, deploy e gerador PDF antes de escolher dependências. Não presuma acesso ao Xano remoto, identidade/CRMV ou modelo PDF que não estejam confirmados. Gere `proposal.md`, `design.md`, `tasks.md` e delta specs conforme OpenSpec instalado; registre evidências, decisões, bloqueios e testes. Não altere a implementação nem os endpoints nesta etapa.
