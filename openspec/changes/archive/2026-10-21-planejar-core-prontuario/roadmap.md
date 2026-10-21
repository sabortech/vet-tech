# Plano do núcleo funcional

Este é um mapa de futuras changes, não uma declaração de funcionalidades prontas.
As prioridades representam ordem de construção; todos os itens abaixo integram
o recorte solicitado. Datas e estimativas não foram atribuídas.

## Situação encontrada

| Área | Evidência atual | Falta principal |
|---|---|---|
| Tutor e pets | Specs principais, APIs Xano, telas Reflex e testes existentes | Seleção persistente no contexto da tela e abertura do pet |
| Veterinário | Identidade autenticável, cadastro/login compartilhados e aptidões por catálogo entregues em `unificar-acesso-perfis` | Autorizações individuais e operações clínicas nas próximas etapas |
| Permissões | Tabela `acesso_autorizado` | API, interface, validação por operação e revogação |
| Prontuário | Tabelas clínicas | APIs e telas de registro e consulta por pet |
| Doenças | `doenca` contém `pet_id`; DER descreve catálogo e associativas | Reconciliar modelo, diagnóstico da consulta e evolução por pet |
| Medicamentos | Tabela sem frequência, consulta ou vínculo com doença | Prescrição legível com dose/unidade/frequência/período e vínculos |
| Auditoria | `log_acesso` com `data_hora` do tipo date | Registro automático com horário, proteção e consulta pelo tutor |
| Agendamento | Nenhuma entidade/API/tela identificada | Profissionais compatíveis, disponibilidade e ciclo de reserva |

## Ordem proposta

| Ordem | Prioridade | Change futura | Dependências | Entrega e aceite principal |
|---|---|---|---|---|
| 1 | P0 | `selecionar-alternar-pet` | Cadastro/listagem existentes | Abrir um pet e trocar entre os próprios pets, sem misturar dados nem aceitar pet alheio. |
| 2 | P0 | `unificar-acesso-perfis` | Seleção de pet entregue; decisões de identidade registradas na proposta | Reutilizar `/cadastro` e `/login`, adaptar os campos do cadastro e abrir a área do perfil validado no backend. Na área do tutor, preparar menu retrátil, Início com dados básicos e ações Novo pet em modal/Mudar pet; clínica opcional, um perfil por e-mail, CRMV com validação local e múltiplas espécies/especialidades; testar duplicidades, isolamento e perfil forjado. |
| 3 | P0 | `autorizar-auditar-acesso-pet` | 1 e 2 | Dono concede/revoga acesso individual, backend centraliza checagem, registra logs com horário e permite ao dono consultá-los; testar outro tutor, não autorizado e revogação. |
| 4 | P0 | `registrar-consultar-prontuario` | 3 e definição do formato de prontuário | Seção Consultas apresenta atendimentos e prontuários anexados/vinculados a cada consulta; veterinário registra e tutor consulta por pet, com autoria/auditoria, sem complemento clínico obrigatório. O resumo de Início passa a refletir os atendimentos disponíveis. |
| 5 | P1 | `registrar-doencas-pet` | 4 | Diagnósticos opcionais por consulta, catálogo e histórico de condições por pet, com estados definidos; relações não atravessam pets. |
| 6 | P1 | `prescrever-medicamentos-pet` | 4 e 5 | Prescrição opcional ligada ao pet/consulta e, quando aplicável, à doença; dose, unidade, frequência e período legíveis ao tutor, sem promessa automática de cura. |
| 7 | P1 | `planejar-registrar-vacinas` | 4 | Veterinário estipula datas previstas e registra aplicações; tutor distingue previsto/aplicado e consulta próxima dose, sem exigir vacina em toda consulta. |
| 8 | P1 | `solicitar-exames-pet` | 4 e decisão de arquivos | Solicitação opcional de exames adicionais, posteriormente resultado; vínculo com consulta consistente e consulta pelo tutor, sem confundir solicitado com realizado. |
| 9 | P2 | `agendar-consulta-pet` | 1, 2 e decisão de agenda; integrar com 4 | Escolher profissional compatível com o pet, disponibilidades e agendar conforme o fluxo aprovado; prevenir conflitos e não conceder prontuário automaticamente. |
| 10 | Integração | `validar-core-prontuario` | 1–9 | Percurso completo real com múltiplos tutores, pets e veterinários; isolamento, revogação, complementos opcionais, agenda e persistência comprovados. |

P0 produz o primeiro ciclo de prontuário utilizável. P1 completa os registros
clínicos pedidos. P2 entra depois por depender de regras de agenda e não ser
pré-requisito para registrar um atendimento já realizado; continua no escopo.
As changes 5, 7 e 8 podem avançar independentemente após a 4, evitando editar
simultaneamente os mesmos arquivos compartilhados. Não há delegação automática.

## Contexto de navegação aprovado

O menu lateral retrátil contém **Início, Vacinas, Medicamentos, Doenças e
Consultas**, com **Novo pet** e **Mudar pet** na parte inferior. Todas as seções
usam o pet selecionado; Início resume suas informações disponíveis. Dentro de
Consultas, cada atendimento apresenta os próprios prontuários vinculados.
Não há nova entrada de menu para cada prontuário.

A etapa 2 prepara a estrutura da área do tutor e transfere o cadastro existente
para modal; a troca reaproveita a entrega já arquivada da etapa 1. A etapa 4
implementa o conteúdo de Consultas. As etapas 5, 6 e 7 implementam os conteúdos
de Doenças, Medicamentos e Vacinas e atualizam os resumos de Início. Exames
permanecem como complemento acessível pela consulta na etapa 8; agendamento
integra o fluxo de Consultas na etapa 9, sem acrescentar opções ao menu aprovado.

Preservar essa estrutura nas propostas futuras, com estados vazios honestos
enquanto os módulos não existirem. O formato de arquivo dos prontuários ainda
precisa ser confirmado; a relação obrigatória com a consulta não depende disso.
O menu permanece na etapa completa `unificar-acesso-perfis`, conforme decisão
posterior do usuário; não há entrega separada de menu lateral.

## Decisões de identidade e entrega auxiliar de registros

- Clínica opcional: o domínio atual contém trechos contraditórios; a implementação
  da etapa 2 alinhará a documentação à opção expressa pelo usuário.
- Um perfil por e-mail normalizado, sem tutor e veterinário simultâneos no mesmo
  e-mail; garantir a regra no backend, inclusive em concorrência.
- CRMV com validação local de caracteres, sem consulta externa. O formato proposto
  e sua unicidade por UF estão detalhados em `unificar-acesso-perfis/design.md`.
- Espécies e especialidades múltiplas por referências a catálogos.
- `popular-catalogos-especies-racas` é entrega auxiliar própria, com revisão
  exclusiva dos registros, fontes, simulação e carga idempotente. Pode ser preparada
  antes da etapa 2; coordenar alterações no catálogo compartilhado. A etapa 2
  não exige uma lista ampla, mas precisa de espécies válidas disponíveis para uso.

## Como registrar cada entrega no OpenSpec

Esta change de planejamento usa `skip_specs: true`: organiza o trabalho sem
alterar contratos de software. A primeira change, `selecionar-alternar-pet`,
foi implementada e verificada com testes locais, Xano real e navegador;
suas 9 tarefas estão concluídas e ela foi arquivada em
`openspec/changes/archive/2026-10-14-selecionar-alternar-pet/`, com a spec
`pet-management` sincronizada. A change `unificar-acesso-perfis` foi implementada
com menu, modal, identidade veterinária e backend publicado; ver suas tarefas,
`verification.md` e `smoke-result.json` para as evidências. Aguarda revisão e
arquivamento, com suas delta specs ainda na change. A auxiliar
`popular-catalogos-especies-racas` possui planejamento completo e implementação
ainda não iniciada. As demais changes de execução ainda não foram criadas.
Para cada uma, antes de implementar:

1. Criar a change com `openspec new change <nome>`.
2. Escrever `proposal.md`: resultado observável, escopo e RF/RN relacionados.
3. Escrever deltas em `specs/<capacidade>/spec.md`, reutilizando capacidades existentes.
4. Escrever `design.md` com contratos, decisões, dados, autorização e migração.
5. Escrever `tasks.md` com backend, frontend, documentação e verificação por fatia.
6. Implementar, guardar evidências em `verification.md`, sincronizar specs e arquivar.

Mapeamento inicial de capacidades, sujeito à revisão de cada proposta:

- Etapa 1 modifica `pet-management`; não recriar cadastro de tutor ou login visual.
- Etapa 2 introduz `veterinarian-identity` e revisa os contratos relevantes de
  `tutor-registration`, `pet-management` e `login-screen-presentation` conforme
  a proposta detalhada. Cadastro e login compartilham as páginas existentes;
  o perfil autenticado é identificado pelo backend, e não escolhido no login.
- Etapa 3 introduz `record-access-control`; considerar os requisitos já propostos
  em `assess-project-improvements`, sem tratar aquela change como implementada.
- Etapa 4 introduz `clinical-records`; etapas 5–8 ampliam essa capacidade ou
  criam subcapacidades clínicas se o contrato justificar uma fronteira própria.
- Etapa 9 introduz `appointment-management`, atualizando domínio e DER.
- Etapa 10 é de verificação; usar `skip_specs: true` se não alterar comportamento.

## Regras transversais de aceite

- As mesmas páginas atendem tutor e veterinário; o cadastro varia seus campos
  conforme o perfil, e o login encaminha conforme a identidade validada pelo
  backend. Alterar o perfil na interface não concede permissões.

- RN01–RN05: tutor controla acesso e só vê seus pets; veterinário precisa de
  autorização ativa em cada operação, inclusive em chamadas diretas à API.
- RN06–RN08: ação clínica veterinária gera log imutável e consultável pelo dono.
- RN15–RN18: pet, consulta e autoria têm vínculos válidos; histórico não é apagado.
- Complementos vazios são válidos; item preenchido parcialmente recebe erro de
  validação, sem registros órfãos ou confirmação de sucesso falso.
- Toda operação com pet/consulta/registro recebido do cliente valida propriedade
  e correspondência dos vínculos no backend.
- Alternância de pet não reaproveita formulários nem respostas atrasadas do anterior.
- Menu e Início refletem o mesmo pet ativo; Consultas mantém cada prontuário
  associado ao atendimento correto. Novo pet abre modal, e cancelá-lo não cria
  registro; Mudar pet preserva as validações e a limpeza de contexto existentes.
- Agendamento, consentimento e atendimento são estados separados; o histórico
  permanece no pet quando muda o veterinário ou a autorização é revogada.
- Cada change inclui testes de regras e integração necessários; a etapa 10
  verifica o conjunto, não substitui os testes das etapas anteriores.

## Fora deste recorte

Upload de foto/laudo, notificações automáticas, exportação PDF, login social,
recuperação de senha, administração completa, gestão de clínicas, pagamentos,
telemedicina e aplicativo nativo. Consulta de datas clínicas permanece incluída.
