## Why

O tutor precisa de uma visão inicial que reúna informações relevantes dos seus pets sem precisar abrir cada seção clínica para descobrir o que está registrado. O Dashboard deve facilitar a identificação do pet, resumir dados existentes e direcionar para ações já disponíveis, sem apresentar conclusões clínicas que o sistema não pode sustentar.

## What Changes

- Criar um Dashboard autenticado exclusivo para o perfil tutor, com escopo alternável entre “Todos os pets” e um pet específico.
- No escopo geral, apresentar cartões resumidos dos pets e eventos ou registros que mereçam atenção, identificados por animal.
- No escopo individual, apresentar perfil do pet no topo e, abaixo, resumos de dados existentes: peso cadastrado, próxima dose de vacina registrada, última consulta finalizada, próximo compromisso registrado e histórico recente de consultas e vacinas.
- Permitir ações rápidas para agendar consulta, abrir o histórico de vacinas e navegar para o prontuário do animal.
- Derivar mensagens de acompanhamento somente de registros e datas existentes, sem declarar que o pet está saudável ou que todos os cuidados estão em dia.
- Não introduzir novos dados clínicos, notificações, métricas de peso, agendamento de exames ou funcionalidades de Exames ainda indisponíveis na interface.

## Capabilities

### New Capabilities
- `tutor-dashboard`: Painel geral e por pet para resumir dados existentes e encaminhar o tutor às ações e seções disponíveis.

### Modified Capabilities
- `authenticated-navigation`: Incluir Dashboard do tutor na navegação autenticada e definir seu escopo sem alterar a seleção atual do prontuário.

## Impact

- Frontend Reflex: navegação do tutor, nova página ou composição do Dashboard e estado do seletor de escopo.
- Backend Xano: adicionar uma leitura por pet no grupo `Clinical`, autenticada para Tutor, com validação `Clinical/assert_owner`, filtros de propriedade em todas as consultas e projeções limitadas aos campos usados pelo Dashboard. O escopo geral continua sendo composto no frontend a partir dos pets retornados pela listagem autenticada; não são necessárias alterações de tabelas nem de APIs existentes.
- Dados sensíveis: o Dashboard exibirá informações de perfil e saúde dos pets. A autorização de leitura permanece vinculada à identidade do tutor e à propriedade do pet no backend; o filtro visual não concede acesso.
- Sem novas dependências ou entidades de domínio previstas. Não há efeito sobre notificações automáticas, que não serão implementadas por esta change.
