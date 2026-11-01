# Organização da aplicação

Este documento registra a estrutura recomendada para o código Python/Reflex do
VetTech. A organização deve evoluir gradualmente conforme cada funcionalidade
for implementada; não é necessário criar pastas vazias nem mover todo o código
existente de uma vez.

## Estrutura recomendada

```text
vet_tech/
├── vet_tech.py             # ponto de entrada Reflex e registro do app/páginas
├── pages/                  # telas associadas a rotas
├── components/             # componentes de interface reutilizados
├── features/               # estado e lógica agrupados por funcionalidade
│   ├── auth/
│   ├── dashboard/
│   ├── tutors/
│   └── pets/
└── shared/                 # integrações e utilitários compartilhados
    └── xano_client.py

tests/
├── unit/
└── integration/

xano/                       # fonte única e autoritativa dos artefatos XanoScript
docs/                       # documentação durável do projeto
openspec/                   # propostas, especificações, designs e tarefas
```

Os diretórios podem ser introduzidos à medida que forem necessários. A
estrutura acima é uma direção para novos módulos, não exige que a aplicação
atual seja reescrita antes de continuar o desenvolvimento.

## Responsabilidade de cada pasta

- **`pages/`**: funções de página e composição das telas ligadas a rotas do
  Reflex. Nem toda view precisa ter uma rota própria; fluxos como alternar
  entre login e cadastro podem ser partes da mesma página.
- **`components/`**: funções que retornam componentes Reflex reutilizáveis,
  como campos de formulário, cabeçalhos e cartões. Evitar colocar aqui estado
  de negócio, chamadas ao Xano ou páginas inteiras que não sejam reutilizadas.
- **`features/`**: estado Reflex, manipuladores de eventos, validações e
  operações específicas de cada capacidade do produto. Agrupar por domínio
  (`auth`, `tutors`, `pets`) mantém próximas as partes que mudam juntas.
- **`shared/`**: código realmente comum a várias funcionalidades, como o
  cliente HTTP do Xano e configuração compartilhada. Não antecipar abstrações
  antes de haver reutilização concreta.
- **`tests/`**: testes unitários e de integração. Testes que usam serviços
  externos devem ser identificados como integração e não depender de produção.

## Convenções de dependência

- `pages/` compõe componentes e conecta a interface ao estado das
  funcionalidades.
- `components/` não deve importar páginas nem controlar autenticação ou regras
  de domínio.
- `features/` pode usar `shared/` para integração, mas regras de autorização
  devem continuar garantidas pelo backend Xano.
- Segredos e credenciais não devem ser escritos em código, páginas,
  componentes ou documentação; usar configuração por ambiente.
- `shared/dates.py` separa datas civis ISO de instantes Xano em milissegundos
  ou ISO com offset. Datas civis mantêm seu dia; instantes são apresentados no
  fuso America/Sao_Paulo. `components/date_input.py` confirma a data selecionada
  em formato brasileiro sem alterar o valor ISO do calendário nativo.
- Manter os artefatos do backend em XanoScript e continuar tratando Xano como
  backend. Esta organização não introduz outro framework ou serviço.

## Aplicação gradual

### Navegação compartilhada do tutor

`components/sidebar.py` contém o catálogo visual único e `layout_com_menu`, usado
por Meus Pets, Configurações, Dashboard e Prontuário. A referência é a sidebar verde existente
com marca, pill ativo branco, ícones e tokens `.sidebar-*` de `assets/vet_tech.css`.
O layout aceita ações por composição; `components/navigation.py` fornece somente
as ações clínicas e o modal, sem criar uma segunda sidebar ou estado de pet.

Ordem das entradas: Dashboard, Prontuário, Vacinas, Medicamentos, Doenças,
Consultas, Exames, Meus Pets e Configurações. Dashboard está habilitado para tutor;
Exames segue sem destino funcional na interface.
O catálogo visual deriva os destinos clínicos da allowlist de
`features/navigation/state.py`, também usada pelo guard do servidor.

`/dashboard` apresenta a visão geral ou individual do tutor a partir de leituras
autenticadas por pet em Xano. “Todos os pets” solicita cada pet próprio com até
quatro chamadas concorrentes; o escopo individual envia somente o `pet_id`
selecionado. Cada consulta clínica também valida a propriedade no backend e aplica
ordenação e limites específicos para próximas datas, pendências e atividade recente.
O filtro do Dashboard é independente de
`selected_pet_id`; somente uma ação explícita de agendamento ou navegação para o
prontuário define o pet de contexto da ação. As projeções derivam idade e mensagens
de acompanhamento dos registros consultados, sem inferir unidade do peso, saúde
geral ou cuidados completos. Falhas de leitura permanecem distintas do estado vazio.
O endpoint fonte está em `xano/api/clinical/tutor/dashboard_GET.xs`, no grupo
`Clinical`, e precisa estar publicado no ambiente Xano usado pela aplicação.
Ele valida o pet com `Clinical/assert_owner` e repete o filtro de propriedade
nas consultas clínicas; a tela não depende das APIs de histórico sem limite.

Prontuário representa Início. As demais seções usam `/prontuario?secao=<chave>`;
as chaves permitidas são `inicio`, `vacinas`, `medicamentos`, `doencas` e `consultas`.
A entrada de página aplica a intenção inclusive em mudança de query e histórico
do navegador. O estado clínico mantém seleção, cache e carregamento; o menu não
cria uma sessão paralela nem faz HTTP para renderizar ou alternar expansão.

`NavigationState.sidebar_preference` conserva a preferência desktop existente;
`drawer_open` é transitório e independente, abaixo de 768 px. O guard de
Configurações valida o destino exato e só o executa depois do descarte confirmado.
As páginas compõem as dependências para evitar o ciclo sidebar → pets → sidebar.

O arquivo `vet_tech/vet_tech.py` atualmente concentra a entrada do app, estado,
comunicação HTTP, páginas e componentes. Novas funcionalidades podem ser
separadas por domínio sem exigir uma migração total imediata. Ao extrair um
módulo, preservar os fluxos existentes e verificar imports, registro de rotas
e build do Reflex.

Os artefatos XanoScript oficiais ficam somente em `xano/`. Não criar nem manter
cópias de `api/`, `table/`, `function/`, `workspace/`, `addon/` ou `ai/` na raiz.
Se arquivos XanoScript aparecerem na raiz, consolidar suas alterações com a
versão autoritativa em `xano/` antes de remover a cópia; não manter duas árvores
de workspace.

### Assistente n8n

`features/support_chat/state.py` fornece o mixin de conversa do State existente;
`shared/n8n_client.py` contém transporte HTTP e validação de contrato. O wrapper
global publica um formulário Reflex oculto, sem credenciais, e os assets mantêm
somente apresentação, animação e histórico visual. Nome, perfil, token e contexto
de envio são derivados pelo servidor. Ver `docs/n8n-chat.md` para configuração e
limites de publicação/validação.
