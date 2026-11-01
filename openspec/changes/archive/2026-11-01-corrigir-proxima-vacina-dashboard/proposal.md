## Why

O tutor relata que uma vacina cadastrada não aparece como próxima vacina no Dashboard. O comportamento esperado já está definido na change `dashboard-tutor`: mostrar a próxima dose registrada quando aplicável. É necessário localizar e corrigir a divergência entre registro, resposta autenticada e cartão, sem ampliar os dados cadastrais exibidos.

## What Changes

- Reproduzir a ausência comparando próxima dose, pet associado, data atual em America/Sao_Paulo, histórico publicado e resposta do Dashboard.
- Corrigir a camada responsável pelo desaparecimento de uma próxima dose válida, preservando o resumo e o layout atuais.
- Garantir nome e data da próxima dose mais próxima, incluindo hoje, nas visões geral e individual.
- Garantir estado vazio legível quando não houver próxima dose futura e distinção entre ausência, falha e data ultrapassada.
- Adicionar regressões para o caso confirmado e verificar API, projeção e interface.
- Revisar o contrato de datas do cadastro de pet, atendimento, agenda e Dashboard: datas sem horário em ISO `AAAA-MM-DD` na comunicação, apresentação brasileira e instantes com fuso explícito.
- Corrigir a ordenação da atividade recente usando datas técnicas antes da formatação; a reprodução local mostrou vacina antiga antes de consulta recente.
- Conferir os demais registros cadastrados que não entram no resumo e registrar separadamente omissões intencionais e defeitos, sem acrescentar automaticamente novos cartões.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma mudança de requisito: correção do contrato de próxima vacina já definido em `dashboard-tutor/specs/tutor-dashboard/spec.md`. `skip_specs: true` evita duplicar essa capacidade, ainda pendente de incorporação às specs principais.

## Impact

Áreas candidatas: `xano/api/clinical/tutor/dashboard_GET.xs`, resposta publicada, `vet_tech/features/dashboard/state.py`, `vet_tech/components/dashboard.py`, formatação/entrada de datas no cadastro e no fluxo clínico e testes existentes. A correção deve limitar-se às divergências reproduzidas, preservando os tipos atuais do Xano. Há outra fonte `xano/api/clinical/tutor_dashboard_GET.xs` declarando o mesmo endpoint; identificar qual é utilizada na publicação antes de escolher o arquivo a corrigir.

Relaciona-se a RF04 e RN05. Mantém autenticação e propriedade no backend, isolamento por sessão e pet, consentimento e auditoria existentes. Não altera registros para fabricar uma próxima dose, não envia notificações nem amplia acesso veterinário.

Não inclui novos campos cadastrais no Dashboard. As pendências remotas e de navegador de `dashboard-tutor` permanecem independentes. A causa do caso relatado ainda não foi confirmada; o registro do usuário não foi consultado com autenticação nesta análise.
