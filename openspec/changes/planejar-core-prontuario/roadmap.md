# Plano do núcleo funcional

Este é um mapa de futuras changes, não uma declaração de funcionalidades prontas.
As prioridades representam ordem de construção; todos os itens abaixo integram
o recorte solicitado. Datas e estimativas não foram atribuídas.

## Situação encontrada

| Área | Evidência atual | Falta principal |
|---|---|---|
| Tutor e pets | Specs principais, APIs Xano, telas Reflex e testes existentes | Seleção persistente no contexto da tela e abertura do pet |
| Veterinário | Tabela `veterinario`, ainda `auth = false` | Identidade, cadastro/login, unicidade e aptidão por espécie |
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
| 2 | P0 | `unificar-acesso-perfis` | Decisões de clínica/CRMV e identidade com dois perfis | Reutilizar `/cadastro` e `/login`, adaptar os campos do cadastro, autenticar tutor/veterinário no backend e abrir a área correta; incluir espécies/especialidades e testar duplicidades, isolamento e perfil forjado. |
| 3 | P0 | `autorizar-auditar-acesso-pet` | 1 e 2 | Dono concede/revoga acesso individual, backend centraliza checagem, registra logs com horário e permite ao dono consultá-los; testar outro tutor, não autorizado e revogação. |
| 4 | P0 | `registrar-consultar-prontuario` | 3 | Veterinário registra consulta e tutor a vê no histórico do pet; sem complemento clínico obrigatório, com autoria e auditoria desde o primeiro endpoint. |
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

## Como registrar cada entrega no OpenSpec

Esta change de planejamento usa `skip_specs: true`: organiza o trabalho sem
alterar contratos de software. As dez changes de execução ainda não foram criadas.
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
- Agendamento, consentimento e atendimento são estados separados; o histórico
  permanece no pet quando muda o veterinário ou a autorização é revogada.
- Cada change inclui testes de regras e integração necessários; a etapa 10
  verifica o conjunto, não substitui os testes das etapas anteriores.

## Fora deste recorte

Upload de foto/laudo, notificações automáticas, exportação PDF, login social,
recuperação de senha, administração completa, gestão de clínicas, pagamentos,
telemedicina e aplicativo nativo. Consulta de datas clínicas permanece incluída.
