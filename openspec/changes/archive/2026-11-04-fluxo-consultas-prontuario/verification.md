# Verificação de fluxo-consultas-prontuario

## Resultado — 21/10/2026

Backend publicado no workspace **167758**, instância `x8ki-letl-twmt.n7.xano.io`, perfil `vetech`, branch padrão configurada. Pacote: 32 documentos, com três tabelas novas, sete atualizadas, seis helpers, um grupo e quinze endpoints. Preview final: **No changes to push**. Fontes/hashes em `bundle-manifest.json`.

Frontend integrado e verificado **localmente** em Reflex 0.9.11, Windows, servidor de produção e Chrome headless. Não houve publicação de site em hospedagem externa. Servidores temporários dos testes encerrados.

Relatório sanitizado: `smoke-result.json`. **180 verificações reais de API/dados/setup/limpeza** e **20 verificações registradas de navegador**, com resultado final aprovado. Esses números incluem preparação e conferência de fixtures, não 180 cenários independentes do produto. Falhas iniciais corrigidas permanecem no histórico privado; aprovação considera a repetição após a correção.

Suíte local final: **96 testes unitários passaram** e `reflex compile --dry` passou. Estado usa HTTP mockado; validação/projeção executam o JavaScript real das Lambdas com Node. Verificações remotas usam HTTP/tokens reais e o navegador usa os eventos Reflex contra esse backend. A revisão final de datas/dados básicos e descarte de leitura atrasada após negação também recebeu testes unitários e compilação.

## Inventário e integridade

Inventário somente de leitura pré-publicação: `.venv/clinical-inventory/20261021T183133439341Z/`. Sete tabelas clínicas/permissões vazias, três pets, um veterinário e três tutores; nenhum conflito de referência/consentimento duplicado. A divergência anterior de schema de `veterinario` foi preservada: essa tabela não integra o bundle.

Baseline privado das 16 tabelas antes das fixtures: `.venv/clinical-smoke/20261021-publish/baseline.json`. Conferência final: todos os IDs/digests anteriores intactos, nenhum ID de fixture remanescente e nenhuma trava residual. Contadores de sequência não foram resetados.

Foram usadas duas identidades de tutor, duas veterinárias, três pets e no máximo **30 consultas sintéticas**. Referências, complementos e logs pertenciam somente às fixtures. O ledger registrou IDs; limpeza verificou ausência no baseline e referências antes de excluir. Para paginação, somente agendamentos sintéticos pendentes foram reassociados ao mesmo profissional. O teste de tutor sem pets mudou temporariamente o dono de um pet sintético e restaurou-o. Nenhum email/notificação foi enviado. Credenciais das fixtures foram retiradas do ledger após limpar.

## Cobertura

| Contrato | Evidência |
| --- | --- |
| Identidade/propriedade | Tokens de perfis cruzados, pet de outro tutor, outro profissional autorizado tentando escrever consulta alheia; negação sem dados alheios |
| Consentimento | Concessão atômica, vínculo único, revogação durante atendimento, reativação e disputa real revogar/finalizar com ordem dos logs conferida |
| Auditoria | Leituras/gravações; tutor dono lê, tutor alheio não; PUT/DELETE públicos bloqueados; falha de auditoria reverte estado/publicação |
| Agendamento | 08h/17h, passado/faixa externa/incompatibilidade, mesmo ID no reenvio, chave divergente, disputas por profissional/pet e mesma operação simultânea |
| Agenda | 26 pendências reais: 25 + 1 páginas; ordem cronológica, mesmos IDs no calendário, pendência atrasada e resposta reduzida sem consentimento; fuso validado pela Lambda real local |
| Início/retomada | Começo antes do horário, reenvio preserva início, responsabilidade/consentimento e bloqueio de finalizada |
| Rascunho | Recuperação, versão obsoleta, gravações simultâneas com um vencedor, IDs forjados, ocultação do tutor e reconciliação local após timeout |
| Complementos | Publicação real de vacina, medicamento decimal contínuo, doença e exame solicitado sem arquivo; grupos vazios; datas, linhas e exame realizado validados pelo código real da Lambda nos testes locais |
| Evolução/legado | Publicação retroativa não regride condição; duas evoluções preservadas; isolamento por pet; catálogo normalizado sem sobrescrever; prescrição inteira legada permanece sem dose/origem inventada; inventário testa associações não comprovadas |
| Atomicidade | Falha depois de complemento válido: comparação administrativa confirmou complementos, consulta e rascunho inalterados; falha de log e finalização simultânea sem duplicação |
| Leitura | Mesmos IDs/origens no histórico/seções; consulta completa e vacina lidas na interface; tutor conserva histórico após revogar |
| Tutor | Modal sem pet global, Voltar preserva campos, consentimento antes de confirmar, reserva para A preserva B no dashboard, Escape/foco e ausência de opções fictícias sem pets |
| Veterinário | Horários/Consultas, Hoje, dia vazio, URL direta, começo/retomada, rascunho/finalização, descarte explícito, desktop/celular e correção de rolagem horizontal |
| Sessão | Logout/troca de perfil no navegador; expiração, resposta antiga, troca de pet e negação durante leitura pendente nos testes de estado |

Não havia exame/arquivo real anterior a migrar ou baixar. A compatibilidade de arquivos foi conferida pela permanência do campo attachment, tipo, visibilidade e estilo, sem excluir campo/arquivo. Não declarar teste de download de arquivo legado inexistente.

## Correções e limites

- O primeiro import recusou sintaxe compacta e o input reservado `now`; corrigidos e validados com o parser oficial. Preview não substitui parser/runtime.
- Criação de consentimento/condição não lê `.id` de null. Reenvio projeta explicitamente o hash interno; agenda declara `error: null`. Casos foram corrigidos e repetidos.
- Reserva adquire chave técnica zero antes da trava do pet; sob concorrência responde 400 de negócio em vez de erro interno de índice. Índices únicos confirmados remotamente em oito tabelas.
- Cliente aguarda/repete somente 429, no máximo duas repetições, para o plano gratuito. Não repete timeout/5xx automaticamente; reserva mantém chave e atendimento reconcilia versão/estado.
- Inputs têm rótulos associados; cabeçalhos/paginação respondem ao celular. Agendamento, data clínica e início/fim reais são distintos. Dados básicos autorizados do pet aparecem no histórico prévio e atendimento.
- Attachment opcional é normalizado como anulável pelo importador; fonte final explicita `attachment? arquivo?`. Tipo, estilo único, visibilidade e conteúdo são preservados. Reposição via API JSON removia filtros e foi descartada. Depois de limpar as fixtures, schema canônico reaplicado com sucesso; trim de `tipo`/`resultado` confirmado. Preview final sem diferenças. Nenhum DROP_FIELD foi executado.
- Não há duração, cancelamento/remarcação, reabertura de finalizada, arquivo obrigatório ou atualização posterior de exame finalizado nesta entrega, conforme o escopo aprovado.

## Reexecução

`scripts/clinical_smoke.py`: setup, teste e cleanup por `--run`, com baseline/ledger privado. `clinical_smoke_{concurrency,atomicity,revocation,pagination,compatibility,rollback}.py` preservam os casos adicionais; `clinical_browser_*.py` preservam percursos com `--run`, `--app-url` e `--browser-executable`.

Nova escrita exige escopo autorizado, run novo e inventário revisado. Não reutilizar o ledger limpo. Executar telas antes da carga final de paginação e respeitar 30 consultas. Playwright é ferramenta de desenvolvimento, não dependência de produção. Nunca usar contas/pets reais como fixtures.

Sem commit/push Git ou arquivamento automático. Change permanece aberta para revisão.
