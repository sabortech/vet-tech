# Design

Situação inicial e decisões de planejamento abaixo; resultado implementado em `verification.md` e `smoke-result.json`. Backend publicado no workspace revisado; frontend validado localmente. Sem publicação de site externo nem arquivamento automático.

Concretização: `ClinicalMixin` compõe a única sessão. Reserva usa trava técnica zero antes da trava do pet para responder conflitos de negócio sob concorrência; demais operações clínicas usam trava por pet. Cliente repete somente 429 de forma limitada para a conta gratuita. Exame mantém attachment opcional explicitamente anulável, sem excluir campo/arquivos; schema final preserva filtros e corresponde ao remoto no dry-run.

## Context

Ver `proposal.md` para motivação e escopo. A aplicação usa Reflex e Xano; `pages/profile.py` compõe as áreas, `components/navigation.py` contém o menu e `features/auth/state.py` mantém a sessão e a seleção segura de pet. A área veterinária ainda é uma apresentação sem agenda. As seções clínicas do tutor são placeholders.

Os schemas locais já contêm `consulta`, `vacina`, `medicamento`, `doenca`, `exame`, `acesso_autorizado` e `log_acesso`. Não existem APIs de atendimento nem associativas `consulta_doenca` e `pet_doenca`. `consulta` só tem data, motivo, diagnóstico e observações, sem estado ou horário; vínculos estão opcionais. Medicamento usa dosagem inteira, sem unidade/frequência/autoria/consulta; `doenca.pet_id` diverge do catálogo reutilizável do domínio; `log_acesso.data_hora` é date. `exame` tem referência a consulta e arquivo, com divergência remota prévia registrada em outra entrega. Tabelas existentes não provam funcionalidade pronta nem ausência de dados legados.

## Goals / Non-Goals

**Goals:** fechar o percurso agendar → atender → finalizar → acompanhar, com consentimento prévio, publicação consistente e isolamento por perfil/pet. Organizar os trabalhos em etapas verificáveis dentro desta única change, reutilizando autenticação, catálogos e composição existentes.

**Non-Goals:** dependências de calendários externos, envio de notificações, arquivo obrigatório, grade/duração de disponibilidade, cancelamento/remarcação, reabertura de finalizadas ou edição clínica pelo tutor. Não migrar a aplicação para outra tecnologia nem reescrever autenticação por conveniência.

## Decisions

### 1. Decisões confirmadas e padrões propostos do MVP

Confirmado pelo usuário: o tutor agenda para seu pet com um veterinário e libera informações previamente, em horário livre de 08h a 17h. A entrada fica no dashboard/tela inicial do tutor e abre pop-up em duas etapas: calendário para dia e, depois, pet e motivo. Preservar a seleção de horário na primeira etapa e a escolha do profissional compatível na segunda, sem adicionar uma terceira etapa. No menu lateral veterinário, Horários abre tela de calendário vertical e Consultas mostra próximos atendimentos, com Começar consulta levando a outra tela sem trava pelo relógio. O prontuário é preenchido na plataforma e persistido no banco para leitura posterior do tutor.

Padrões desta proposta, explícitos para revisão: 08h e 17h são limites inclusivos; precisão de minutos; fuso do serviço `America/Sao_Paulo`; agendar no passado é inválido, mas iniciar antes do horário agendado é permitido. Não introduzir restrição por dia da semana, feriado ou jornada individual que o usuário não definiu. Sem duração acordada, conflito significa mesmo instante de início para profissional ou pet, não sobreposição de intervalos; mostrar essa limitação na revisão do produto, sem simular horários garantidamente livres por duração.

Manter o nome Consultas no menu do tutor; dentro dele apresentar agendamentos, histórico finalizado, detalhes do prontuário e acessos. O botão principal de agendar pertence ao dashboard e funciona sem pet aberto; o animal é escolhido dentro do pop-up. Não criar uma segunda seção Prontuários que duplique conteúdo. O menu veterinário separa Horários, com calendário vertical por horário, de Consultas, com lista de próximos atendimentos e pendências ainda não finalizadas. Motivo e diagnóstico em texto são obrigatórios para encerrar; observações e retorno são opcionais. Complementos são opcionais, com validação das linhas incluídas. Não há expiração automática da autorização ao encerrar: o dono pode revogá-la.

### 2. Consulta como identidade única da reserva e do atendimento

Estender `consulta`, evitando duplicar pet/profissional em uma tabela de agendamento independente. Novos campos: `status`, `agendada_para` timestamp, `fuso`, `iniciada_em`, `finalizada_em`, `data_atendimento`, `retorno_previsto`, `versao`, `rascunho` e identificação idempotente do pedido. Preservar `data`, `motivo`, `diagnostico`, `obs` e IDs legados. Novas consultas exigem pet e veterinário; a sessão determina os atores. Se legado impedir obrigatoriedade global imediata, aplicar exigência nas operações novas e registrar lacunas, sem inventar vínculos.

Estados e transições:

```text
agendada -- Começar consulta --> em_atendimento -- Terminar consulta --> finalizada
                                   |
                                   +-- Salvar rascunho --> em_atendimento
```

`agendada_para` nunca é reescrita pelo início real. Começar é transição idempotente e pode ocorrer antes da data/hora agendada; não é necessário agendador de tarefas ou evento de relógio. Finalizada é somente leitura nesta entrega. Fim real e auditoria vêm do servidor; datas clínicas são campos próprios, sem confundir prescrição futura com evento já realizado.

Reservas usam índices únicos de profissional/instante e pet/instante para novos registros, ou chaves técnicas equivalentes se os nulos/legado exigirem. A chave idempotente é escopada ao ator e operação e guarda hash do pedido; mesma chave com conteúdo diferente retorna conflito. A identificação é gerada antes do envio e reutilizada após timeout, não a cada tentativa. Agendar grava consulta e concessão de acesso na mesma transação; falha não pode reativar autorização.

### 3. Consentimento prévio e autoria no backend

O agendamento exibe: confirmar libera a esse veterinário os dados básicos e histórico publicado do pet, inclusive antes da consulta. Não exigir uma segunda autorização separada para o mesmo agendamento. `acesso_autorizado` passa a ter unicidade por pet/veterinário, estado ativo/revogado, timestamps e origem da concessão; concessões, revogações e reativações ficam rastreáveis.

Funções compartilhadas Xano verificam token da entidade correta e dono ou consentimento ativo. A agenda lista apenas reservas do profissional autenticado. Sem consentimento, retorna somente informações mínimas de compromisso, como horário/estado e identificador da reserva; não deve expor histórico ou manter o nome do pet em resposta clínica não autorizada. A responsabilidade pela consulta é verificada adicionalmente em início, rascunho e finalização. Um outro veterinário autorizado pode ler o histórico publicado, mas não alterar aquele atendimento.

Revogação e mutações clínicas devem ser serializadas pelo mesmo vínculo de autorização ou controle equivalente: não basta uma checagem distante da gravação. Após revogar, uma nova operação não pode usar cache de consentimento antigo. Rascunhos ficam protegidos e recuperáveis se o dono reativar acesso; nada publicado é excluído. Tutor lê apenas seus pets e não modifica registros clínicos.

`log_acesso` recebe timestamp com precisão de hora, consulta opcional, ação e identificação da operação. Auditar leituras clínicas autorizadas, salvamentos e finalização; log de ação bem-sucedida integra a transação correspondente. Repetição de uma finalização não duplica o evento. Não oferecer APIs de alteração/exclusão de logs; tutor consulta apenas eventos de seu pet. Não retornar dados sensíveis se a auditoria da leitura falhar.

### 4. Rascunho separado dos registros publicados

Guardar o rascunho estruturado na consulta, com IDs estáveis de linhas e versão otimista. Salvar explicitamente o conjunto; exibir última confirmação e alterações locais pendentes. Na retomada, carregar a versão confirmada do banco. Dois editores com versões distintas recebem conflito; não aplicar último envio silenciosamente.

Consultas agendadas/em atendimento aparecem ao tutor apenas como reserva e estado, sem diagnóstico ou complementos não publicados. A tela do responsável pode ler seu rascunho após validar atribuição e consentimento. Leituras consolidadas nunca consultam rascunhos.

Na finalização, o backend bloqueia/condiciona a versão da consulta, revalida consentimento, vínculos e campos, persiste cabeçalho e complementos, atualiza condições do pet, grava auditoria e muda o estado em uma transação. Falha reverte todo o conjunto e mantém o rascunho. Repetir o mesmo pedido devolve o resultado final existente somente após as verificações de acesso. Linhas de origem têm unicidade por consulta/identificador de linha para impedir duplicação.

Alternativa rejeitada: inserir diretamente em vacinas/medicamentos do pet a cada digitação, pois exporia conteúdo incompleto e dificultaria rollback. Não depender de limpeza posterior para corrigir publicação parcial.

### 5. Dados clínicos e projeções consolidadas

| Entidade | Evolução prevista | Fonte para o tutor |
|---|---|---|
| Consulta | Datas, estado, motivo, diagnóstico, observações, autoria, retorno opcional | Detalhe em Consultas após finalizada |
| Vacina | Manter aplicação/lote/próxima dose; adicionar consulta e linha de origem | Vacinas e detalhe da consulta usam a mesma linha |
| Medicamento | Preservar dosagem antiga; adicionar dose decimal/unidade, frequência, via, tipo, período, veterinário, consulta e linha | Medicamentos e detalhe usam a mesma prescrição |
| Doença | Catálogo reutilizável; retirar dependência lógica de pet no catálogo novo, preservando legado | Nome padronizado e referências, sem condição global |
| Consulta-doença | Diagnóstico datado e estado registrado no atendimento | Evidência histórica imutável por consulta |
| Pet-doença | Condição individual com estado e versão, ligada às evoluções publicadas | Estado atual e histórico acessível em Doenças |
| Exame | Solicitação/realização, tipo, datas e resultado em texto; manter arquivo legado opcional | Dentro da consulta, sem exigir arquivo |

Nomear vacinas e prescrições em texto nesta primeira entrega, sem criar catálogo médico fictício ou recomendações automáticas de dose. Para doença, oferecer busca no catálogo e criação autenticada de nome/descrição mínimos quando ausente, com normalização e unicidade; atualizar condição somente para o pet autorizado. Preservar descrição, tipo e gravidade existentes. Não mudar a condição de outro pet que referencia a mesma doença.

Evoluções de doenças usam data clínica e instante de publicação para ordenar o histórico; o estado atual é o da evolução publicada de data clínica mais recente, com desempate determinístico pela publicação. Uma consulta antiga finalizada depois não deve regredir o estado mais recente. Concorrência no mesmo pet/condição exige serialização ou versão também nesse vínculo.

Datas de aplicação/diagnóstico/realização não podem indicar evento realizado no futuro; próxima dose não antecede aplicação; fim de prescrição não antecede início; retorno não antecede atendimento; solicitação de exame não pode ser posterior à realização. Medicamento contínuo permite fim ausente; os demais exigem período preenchido. O início de prescrição pode ser futuro e não é apresentado como administração realizada. Não calcular tratamento ou cura automaticamente.

A solicitação de exame pode terminar sem resultado; resultado já disponível pode ser registrado durante a consulta. Inclusão posterior de resultado em consulta finalizada não integra esta entrega, que não permite reabertura. Exames legados avulsos e arquivos existentes permanecem preservados. A implantação deve atualizar os trechos de documentação que exigem arquivo mínimo para refletir a decisão de prontuário estruturado sem upload.

Todas as projeções do tutor usam os mesmos IDs publicados e filtram proprietário e pet no backend. Para entradas novas, exigir consulta finalizada; entradas legadas sem consulta usam caminho explícito de histórico legado, sem fabricar publicação/associação. Expor paginação/ordenação por data; não devolver dados clínicos na busca de profissionais.

### 6. Contratos de API propostos

Criar grupos próprios para agenda/prontuário sob `xano/api/`, preservando `vettech-pets` e Authentication. Nomes finais dos grupos podem ser definidos na implementação sem mudar os contratos abaixo.

| Operação | Ator e verificação | Comportamento |
|---|---|---|
| GET profissionais por espécie | Tutor, dono do pet alvo | ID, nome, CRMV/UF e aptidões pertinentes; sem email/hash |
| POST consultas | Tutor e pet próprio | Reserva idempotente e consentimento transacionais |
| GET consultas do pet | Tutor e propriedade | Agenda/estado e registros finalizados, nunca rascunho |
| GET agenda por dia | Veterinário autenticado | Reservas do dia no fuso do serviço para calendário vertical em Horários |
| GET próximas consultas e pendências | Veterinário autenticado | Lista paginada por data/hora para Consultas; inclui agendadas atrasadas e em atendimento, sem finalizadas |
| POST consulta/iniciar | Responsável e consentimento | Transição atômica sem bloqueio pelo relógio |
| GET/PATCH consulta/rascunho | Responsável, consentimento e versão | Retomada e salvamento de dados não publicados |
| POST consulta/finalizar | Responsável, consentimento e versão | Publicação atômica e resposta idempotente |
| GET histórico/detalhe/seções | Dono ou veterinário autorizado | Mesmos registros publicados; auditoria para profissional |
| GET/POST catálogo de doenças | Veterinário autorizado no contexto | Buscar/criar referência sem regravar outras condições |
| GET/PATCH acessos e GET auditoria | Tutor e propriedade | Gerir somente o vínculo do pet e consultar eventos |

Respostas distinguem validação, sessão inválida, acesso negado, versão/horário em conflito e erro transitório. Um ID alheio retorna erro genérico sem confirmar existência. Nunca confiar em `tutor_id`, `veterinario_id` ou perfil enviados como autorização. Timeout de escrita não implica rejeição: consultar estado/resultado idempotente antes de reenviar.

### 7. Composição Reflex sem duplicar sessão

Reutilizar a sessão em `features/auth/state.py`, seu descarte por gerações e `_clear_pet_context()`. Agrupar agenda/atendimento e leituras clínicas em módulos de features próprios; não concentrar todos os formulários no arquivo de autenticação. A implementação deve seguir as skills Reflex disponíveis para APIs e compilação.

Tutor: disponibilizar Agendar consulta em Início/dashboard fora do bloco que exige pet previamente selecionado. Usar diálogo acessível de duas etapas, com título/indicador de progresso, Continuar, Voltar, Cancelar e confirmação final. Etapa 1 apresenta calendário de dias e campo de horário de 08h a 17h; avançar exige ambos válidos. Etapa 2 apresenta lista de pets próprios, motivo e profissional que atende a espécie do pet escolhido, além de resumo de data/hora e informação de liberação prévia. A consulta e a autorização só são criadas na confirmação final. Não reservar parcialmente ao escolher dia ou avançar.

O pop-up tem estado próprio de dia/hora, etapa, pet e profissional; não depende do pet global já aberto e não o troca silenciosamente ao confirmar. Voltar preserva os dados; mudar o pet dentro do pop-up invalida profissional incompatível e respostas pendentes da busca anterior. Fechar sem enviar descarta o rascunho e retorna foco ao botão. Em envio, impedir duplicidade e fechamento que sugira cancelamento de uma gravação já enviada; após timeout reconciliar resultado pela chave idempotente. Sem pets, mostrar orientação na etapa 2 e não permitir confirmar. Limpar o diálogo em logout/troca de identidade.

Consultas do tutor mostra os agendamentos do pet selecionado, finalizadas e Acessos, inclusive reservas originadas pelo pop-up global. Vacinas/Medicamentos/Doenças usam as projeções compartilhadas com datas/autoria e origem. A criação pelo diálogo não deve acoplar a reserva a uma leitura clínica ou exigir seleção global anterior.

Veterinário: menu lateral contém Horários e Consultas, além das ações de sessão. Horários abre tela de calendário vertical no conteúdo principal: eixo de horários, dia inicial Hoje, controle de data/dia anterior/próximo e cartões posicionados pelo início agendado. A disposição vertical é visual, não uma grade de disponibilidade nem duração de consulta. Consultas abre lista cronológica dos próximos atendimentos, independente da data exibida em Horários, com pendências agendadas atrasadas e atendimentos em andamento identificados; finalizadas não permanecem na lista de pendências. Os dois componentes consomem as mesmas reservas e estados, com invalidação/atualização após início ou finalização.

Começar consulta e Retomar ficam na lista Consultas, não no calendário de Horários. Abrir histórico é ação própria e auditada. Começar/Retomar abre `/atendimento/[consulta_id]` com cabeçalho do pet, dados gerais, complementos repetíveis, Salvar rascunho e Terminar consulta. Voltar à lista preserva seu contexto; acesso direto à rota repete validação, sem depender de ter passado pela lista.

Começar consulta leva a outra tela, não ao pop-up de agendamento. Recolher o menu preserva seleção e seção ativa. Diálogo, calendário vertical e listas funcionam por teclado e em tela estreita; não substituir por biblioteca externa sem necessidade. Mostrar carregamento, vazio, conflito e erro com recuperação. Antes de sair do atendimento com mudanças locais, confirmar descarte; ao salvar/finalizar, bloquear clique repetido e aguardar resultado confirmado. Ao trocar pet clínico, consulta ou sessão, invalidar leituras pendentes e não reaproveitar formulário de outro contexto; a escolha do pet do diálogo permanece separada da seleção clínica global. Uma falha de permissão limpa o conteúdo clínico exibido e orienta a verificar consentimento, sem apagar o rascunho persistido.

## Risks / Trade-offs

- [Entrega atravessa módulos antes separados] → implementar nas etapas do tasks.md, com verificação por contrato e percurso completo; não marcar o fluxo entregue com apenas tabelas ou telas.
- [Concorrência em agenda, revogação ou finalização] → índices únicos, idempotência, versão e operações transacionais; testar disputa real antes de afirmar proteção efetiva.
- [Plano Free limita ambiente isolado] → testes locais de regra/estado e plano de smoke controlado revisável; não exigir compra de plano nem declarar testes remotos que não ocorreram. A dispensa anterior de testes do catálogo não autoriza automaticamente dispensar verificação clínica.
- [Dados legados divergentes] → inventário específico, backup privado, mapeamento revisado, migração aditiva e interrupção diante de ambiguidades.
- [Sem duração, cancelamento ou remarcação] → o MVP não resolve toda a gestão de agenda; documentar que só impede início idêntico. Não introduzir silenciosamente duração de 30/60 minutos.
- [Rascunho contém informação sensível] → nenhuma leitura pública/tutor, verificação a cada acesso e limpeza de memória da interface ao mudar contexto.

## Migration Plan

1. Antes de alterar schemas, inventariar somente as tabelas clínicas/permissões e referências necessárias: contagens, nulos, estados, datas, duplicidades e diferenças entre script e fonte publicada; guardar backup/digests privados sem exibir informações de saúde ou credenciais.
2. Criar bundle aditivo dos schemas/funções/APIs da change e executar dry-run restrito. Não publicar toda a árvore nem corrigir a divergência antiga de `exame` sem comparar campo a campo.
3. Migrar associativas e chaves apenas com correspondência comprovada. Manter `doenca.pet_id` e dosagem legada até reconciliação; não converter datas sem hora para horários inventados de agenda/auditoria. Se não houver dados clínicos, registrar o fato em vez de pressupor.
4. Verificar contratos locais, compilação Reflex e fluxo por papéis. Preparar smoke real com fixtures sintéticas identificadas e plano de remoção apenas delas; apresentar destino, dados e efeitos antes de qualquer publicação ou teste com escrita no workspace compartilhado. Definir estratégia compatível com o plano disponível sem usar dados reais como fixtures.
5. Publicar somente após revisão do bundle concreto e autorização da implantação; verificar preservação dos digests anteriores, agendamento/consentimento, agenda, início manual, rascunho, finalização e leituras nas seções. Registrar o que foi exercitado e o que estiver bloqueado; nenhum teste omitido equivale a aprovação.
6. Reversão: desabilitar novas escritas do fluxo, preservar consultas/rascunhos/registros já criados e logs; restaurar versão anterior da aplicação/API que não corrompa os campos novos. Não truncar tabelas, apagar histórico nem restaurar snapshot inteiro sobre registros posteriores. Uma reversão de dados requer plano específico e revisão dos registros novos, não exclusão automática.

Atualizar `docs/domain-model.md`, `docs/DOCUMENTACAO.md` e diagrama do modelo durante a implementação; referenciar esta change como plano vigente do fluxo, sem reescrever o roadmap arquivado. Não sincronizar specs principais antes da entrega e revisão.
