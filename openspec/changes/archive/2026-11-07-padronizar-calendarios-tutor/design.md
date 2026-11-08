# Design

## Context

`calendar_panel` e `perimeter_led` em `components/date_input.py` já atendem agenda e atendimento médicos. O agendamento usa grade própria em `booking_dialog`; o cadastro de pet é o único campo de data nativo restante no tutor. Ver motivação em `proposal.md` e estrutura em `docs/architecture.md`.

## Goals / Non-Goals

**Goals:** reutilizar a apresentação e o grid existente sem criar outro calendário, preservando ISO, foco, responsividade e regras de cada domínio.

**Non-Goals:** modificar endpoints, autorização, consentimento, horários do MVP, calendário médico ou regras clínicas não relacionadas.

## Decisions

- Estender `calendar_panel` com parâmetro opcional de bloqueio, leitura de dias indisponíveis e texto de cabeçalho configurável. Defaults preservam os consumidores médicos. Distinguir espaços vazios do mês de dias reais desabilitados para manter datas passadas/futuras legíveis.
- Na etapa 1, `booking_dialog` compõe diretamente `calendar_panel`, com horário, mensagem e Continuar em `extra_action`. Etapa 2 mantém seu conteúdo e eventos. Selecionar dia apenas atualiza o rascunho; o painel permanece aberto.
- Reutilizar `calendar_days` no estado de agendamento e nascimento, acrescentando `disabled` de acordo com cada contexto. Manter mês/ano e seleção independentes. Validar dias, meses/anos e bloqueio de envio no servidor Reflex; preservar validação Xano final.
- Nascimento usa estado próprio no `State` existente, sem abrir o contexto médico. O botão de data no formulário abre diálogo; a seleção fecha somente o diálogo de nascimento, com foco restaurado no campo. Limpar e fechar não submetem o cadastro. Valores opcionais ISO e `date_hint` permanecem.
- Os seletores de ano seguem janela ao redor do ano exibido, como o componente médico; navegar mês/ano não faz HTTP. Painéis usam os tokens globais de tema e classes específicas do tutor.

## Risks / Trade-offs

- [Diálogo de nascimento dentro do modal Novo pet] → testar Escape, fechar e seleção preservando o formulário pai e o foco.
- [Regras distintas entre nascimento e agendamento] → testar futuro/passado, ano bissexto, virada de mês, horário e bloqueio de envio.
- [Alteração em componente compartilhado] → manter defaults e executar regressão de calendário médico e datas.
- [Botões em formulários] → definir `type=button` em controles de calendário e não disparar submit ao navegar.

## Migration Plan

Não há migração de dados. Compilar e testar com API sintética local, preservando/restaurando a configuração frontend do servidor em uso. Atualizar documentação e registrar capturas desktop/mobile/temas e resultados na mudança. A reversão afeta somente componentes, eventos de calendário e CSS.

## Correção do ambiente de testes após tela vazia

O build de produção do teste compartilhava `.web` com o Vite em uso, invalidando imports memoizados de rotas. O roteiro passa a compilar em workspace temporário, com cópia do código/configuração e dos arquivos gerados, reutilizando apenas dependências instaladas e leitura dos assets. Não escreve mais os módulos/rotas/env da aplicação ativa. Um restart do grafo Vite via atualização de mtime da configuração recupera o servidor afetado sem reiniciar backend nem alterar dados.
