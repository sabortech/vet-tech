# Verificação da correção do Dashboard e das datas

## Achados e alterações

A consulta administrativa inicial encontrou uma aplicação cadastrada sem `data_prox_dose`; esse registro não pode gerar uma próxima dose por suposição. O teste posterior, autenticado com conta sintética, confirmou também um defeito independente: mesmo gravando a próxima dose ISO de hoje no pet próprio, a resposta de `tutor/dashboard` trouxe `vacinas: []`.

O endpoint publicado usava nove consultas paginadas com projeção de campos de registro, enquanto sua Lambda consome listas simples. A correção explicita `metadata: false` em cada paginação, mantendo autenticação, helper de propriedade, filtros por tutor/pet, limites e ordenação. A prévia oficial mostrou somente `UPDATE query tutor/dashboard GET`; a publicação aplicou um único documento. Na repetição autenticada, a vacina passou a ser retornada com a data correta, confirmando a causa e a correção.

Na interface, os objetos vazios de próxima vacina e última consulta não tinham as chaves acessadas pelos componentes. A projeção agora fornece campos vazios explícitos, e o cartão informa “Sem próxima dose informada”. A atividade recente ordena datas técnicas antes de formatar o resultado.

`shared/dates.py` separa datas civis de instantes. O cadastro preserva ISO e rejeita data inválida antes do envio. Horários numéricos e ISO com offset usam America/Sao_Paulo na exibição. Os calendários nativos mantêm o valor ISO e exibem uma confirmação brasileira abaixo do campo; a aparência interna do calendário continua dependendo do navegador/sistema operacional.

## Mapa de datas

| Campos | Contrato de entrada/tipo Xano | Exibição |
| --- | --- | --- |
| Nascimento | `data_nasc`, ISO, `date` | DD/MM/AAAA; idade derivada no resumo |
| Aplicação/próxima dose | `data_aplicacao`, `data_prox_dose`, ISO, `date` | DD/MM/AAAA |
| Atendimento/retorno | `data_atendimento`, `retorno_previsto`, ISO, `date` | DD/MM/AAAA |
| Medicamentos | `data_inicio`, `data_fim`, ISO, `date` | DD/MM/AAAA |
| Diagnóstico/evolução | `data_diagnostico`, `data_evolucao`, ISO, `date` | DD/MM/AAAA |
| Exames | `data_solicitacao`, `data_realizacao`, ISO, `date` | DD/MM/AAAA |
| Agenda | dia ISO + horário → `agendada_para`, `timestamp` | DD/MM/AAAA HH:mm no fuso de negócio |
| Início/fim e auditoria | `iniciada_em`, `finalizada_em`, `ocorrido_em`, `timestamp` | DD/MM/AAAA HH:mm no fuso de negócio |

As respostas reais verificadas para nascimento e vacina usam strings ISO; não houve migração ou alteração de tipos. A validação clínica existente exige ISO e rejeita datas inexistentes. Valores civis não são interpretados como timestamps nem como mês/dia.

## Cobertura dos demais resumos

| Registro | Resultado da análise |
| --- | --- |
| Medicamentos e doenças | Ausentes da consulta/projeção atual do Dashboard; permanecem nas seções do prontuário. Sem novos cartões nesta change. |
| Exames solicitados | Aparecem como acompanhamento sem inventar prazo. |
| Exames realizados | Fora da atividade recente atual; disponíveis no histórico. |
| Consultas sem status | Exibidas como legado no histórico, mas excluídas do resumo de finalizadas; não foram reclassificadas nesta correção. |
| Consulta finalizada, próxima consulta/retorno, vacinas | Já previstos no resumo; afetados também pelo problema de retorno paginado do endpoint. |

## Resultados locais

- 206 testes unitários aprovados, incluindo regressões de ordenação, próxima dose, objetos vazios, ISO, bissexto, datas inválidas, ciclo de cadastro e diferenças de fuso.
- `reflex compile --dry`: aprovado.
- `openspec validate corrigir-proxima-vacina-dashboard --strict`: aprovado.
- `tests/integration/dashboard_dates_browser.py`: oito verificações de navegador aprovadas, com Reflex em produção e API HTTP local sintética, em pt-BR e en-US, incluindo fuso Pacific/Auckland. Zero erros JavaScript.
- Navegador verificou Dashboard geral/individual, estado vazio, falha e recuperação, nascimento, agenda e rascunho de atendimento; valores de formulário foram enviados como ISO.
- Os processos temporários do teste foram encerrados. O primeiro roteiro teve falha de seletor duplicado e foi corrigido; só a repetição aprovada conta como evidência.

## Xano real

`tests/integration/run_dashboard_dates_live.py --development` cria fixtures exclusivas e limpa somente os IDs criados, sem remover consultas ou logs. As tentativas antes da publicação reproduziram o retorno vazio; as conferências de limpeza de vacina, pet, reserva de e-mail e tutor passaram em todas elas. Dados e comparações privados ficam em `.venv/dashboard-dates-live/`, sem senhas/tokens nos relatórios públicos.

Bundle preparado: `.venv/dashboard-endpoint-fix/`, com um único endpoint. Nenhum schema, registro ou variável de ambiente integra a publicação. Arquivo canônico: `xano/api/clinical/tutor/dashboard_GET.xs`; o arquivo antigo de nome semelhante não participa do bundle.

## Confirmação final remota

Publicação concluída: somente `GET tutor/dashboard`, sem schemas ou registros no bundle. A repetição real aprovou 11 verificações, incluindo setup/limpeza: aplicação sem próxima dose, nascimento preservado, gravação ISO da próxima dose, retorno autenticado da vacina, projeção de hoje em formato brasileiro, escolha da menor data entre duas doses, negativa sem sessão e limpeza das quatro tabelas de fixtures.

O endpoint não exigiu migração de dados. O registro anterior sem próxima dose permaneceu intacto. As primeiras tentativas e seus resultados negativos estão no ledger privado; apenas a repetição posterior à correção aprovada comprova o contrato final.
