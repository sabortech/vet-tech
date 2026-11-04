# Arquivamento OpenSpec — 04/11/2026

As 11 changes abertas foram arquivadas em `openspec/changes/archive/2026-11-04-<nome>/`, no schema `spec-driven`, após alinhamento com a `main` (`0a412f0`). Artefatos, tarefas e evidências foram preservados.

| Change | Tarefas concluídas |
| --- | --- |
| abrir-chat-mascote | 12/12 |
| carregar-env-local | 4/4 |
| corrigir-contraste-tema-claro | 3/3 |
| corrigir-inicializacao-login-local | 3/3 |
| dashboard-tutor | 8/10 |
| embelezar-card-perfil-veterinario | 2/2 |
| fluxo-consultas-prontuario | 26/26 |
| integrar-chat-n8n | 6/6 |
| redesenhar-atendimento-medico | 22/22 |
| redesenhar-consultas-medico | 13/13 |
| unificar-menus-tutor | 12/12 |

## Consolidação

Os 18 deltas foram consolidados em 13 specs principais, incluindo cinco novas capacidades: agendamento, registros clínicos, chat de suporte, integração n8n e Dashboard do tutor. A correção da inicialização local declara `skip_specs: true` e não possui delta.

A mesclagem preserva requisitos e cenários existentes e reconcilia evoluções posteriores: Dashboard separado do Prontuário, respostas do chat via n8n, paleta clínica por status e distinção entre foto ausente e falha de imagem. Referências operacionais ao fluxo clínico e às evidências do menu foram atualizadas para os caminhos arquivados.

## Pendências preservadas

O arquivamento de `dashboard-tutor` com duas verificações pendentes foi autorizado explicitamente pelo solicitante. As tarefas 1.1 e 3.4 continuam desmarcadas no [arquivo original](../openspec/changes/archive/2026-11-04-dashboard-tutor/tasks.md):

- Validar no Xano real, com sessão de tutor, pet próprio, rejeição de pet alheio e campos/limites da resposta.
- Completar a verificação no navegador com conta sem pets e início do agendamento; a verificação anterior registrou erro de transporte WebSocket.

Arquivar não atesta a conclusão dessas verificações.

## Verificação do arquivamento

- Validação inicial estrita: 11 changes e 19 specs aprovadas.
- Validação final estrita: 24 specs aprovadas.
- Conferência dos requisitos e cenários de todos os deltas e preservação dos títulos anteriores.
- Conteúdo dos 231 arquivos originais das changes preservado byte a byte após a movimentação.
- Nenhuma change ativa após o arquivamento.

Esta operação consolida documentação e caminhos de ferramentas; não publica o frontend nem o backend.
