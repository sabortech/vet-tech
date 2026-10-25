# Design

## Contexto

A rota `/` escolhe entre login e `profile_view()` conforme o estado de autenticação; `/login` também pode exibir o perfil autenticado. O formulário, a lista e as ações atuais ficam em `vet_tech/components/pets.py`, enquanto `vet_tech/features/auth/state.py` coordena o estado e as chamadas ao Xano. Não há sidebar nem tokens CSS centralizados; estilos globais estão em `vet_tech/vet_tech.py`.

O cadastro já envia a imagem pelo campo `foto` e a tabela Xano possui esse campo, mas `list_GET.xs` não o inclui na resposta. O perfil mapeia sexo e data sem normalização visual. As telas Dashboard, Prontuário, Vacinas, Consultas, Exames e Configurações ainda não existem como rotas.

## Objetivos / Fora de escopo

**Objetivos:**

- Remodelar o perfil autenticado existente sem mover a rota nem substituir a lógica de autenticação, cadastro, atualização, upload ou logout.
- Isolar menu e wrapper em um componente compartilhado e estado de navegação independente da lógica de autenticação/pets.
- Apresentar dados de pets de forma legível e responsiva, com foto quando disponível.
- Deixar preparada a integração do componente por telas futuras, sem criar essas telas.

**Fora de escopo:**

- Criar ou renomear páginas, rotas, campos, ações ou endpoints de cadastro.
- Alterar o modelo de dados ou a propriedade da imagem no Xano; somente adicionar o campo já existente ao retorno da listagem.
- Alterar os valores persistidos de sexo ou a semântica dos dados enviados ao backend.
- Implementar funcionalidade para as áreas do menu que ainda não têm tela.

## Decisões

### Componente de navegação e estado

- Criar `vet_tech/components/sidebar.py` com `layout_com_menu(conteudo, pagina_ativa)`. O wrapper compõe uma única árvore de navegação, uma barra superior com o controle sempre visível e o conteúdo da tela; uma página futura poderá integrá-lo passando seu conteúdo e sua área ativa.
- Criar `vet_tech/features/navigation/state.py` para manter o estado da navegação fora de `features/auth/state.py`, respeitando a separação entre UI compartilhada e estado de domínio. A preferência desktop e a abertura transitória do drawer móvel serão estados separados na mesma classe compartilhada.
- A preferência desktop inicia expandida e alterna entre aproximadamente 260 px e 76 px. O drawer móvel inicia fechado e não restaura sua abertura transitória ao carregar ou navegar. O estado compartilhado preserva as mudanças entre telas da aplicação; persistir somente a preferência desktop em `rx.LocalStorage` se a API da versão instalada do Reflex permitir restauração sem flicker. Caso não permita, manter a persistência entre rotas da aplicação, sem introduzir JavaScript ou dependência apenas para persistência.
- O controle fica na barra superior, fora do drawer, para continuar alcançável quando o menu estiver recolhido ou fechado. Em mobile, o drawer usa backdrop; Esc e o backdrop fecham o estado transitório. Itens sem tela usam controle não navegável com indicação discreta “Em breve”.

### Layout e responsividade

- Desktop: raiz flexível, sidebar sem encolhimento e conteúdo com `flex: 1` e `min-width: 0`; largura do menu transiciona sem cálculo manual de margem. A transição de largura e conteúdo usa 250–300 ms com easing.
- Abaixo de 768 px: sidebar vira drawer fixo sobreposto, fechado por padrão; o conteúdo usa 100% da largura. O drawer limita sua largura à viewport e o backdrop fecha o painel.
- Área do perfil: cartões em duas colunas apenas quando a largura útil comportar o formulário e a lista; empilhar em torno de 1100 px. Campos do formulário passam a uma coluna abaixo de 600 px.
- O mascote existente `assets/mascote06.png` é decorativo, com `pointer-events: none`, colocado em camada que não cobre os cartões; reservar espaço no fim do conteúdo e ocultá-lo em telas pequenas.
- A barra lateral e o perfil usam Nunito, já carregada pela aplicação. Tokens CSS ficam centralizados em `assets/vet_tech.css` e cobrem fundo `#F4F5F7`, texto `#1A3629`, verde principal próximo de `#689554`, superfícies, fundo de ícones, campos, bordas, raios e espaçamentos. O arquivo é registrado como stylesheet global no app; componentes consomem os tokens, sem repetir cores soltas. A patinha e “Vet Tech” usam o mesmo token de cor.
- Como os wrappers padrão de layout Reflex não recebem `on_key_down`, a abertura do drawer registra um listener cliente para Esc; fechar o drawer remove o listener e aciona um evento Reflex oculto para manter a alteração de estado no backend.

### Perfil e dados

- Manter `profile_view()` como composição do perfil existente, agora envolvida por `layout_com_menu(..., pagina_ativa="meus_pets")`. O cabeçalho do perfil preserva “Perfil do tutor” e “Sair”; o formulário preserva labels/placeholders, campos e eventos atuais.
- O card de cadastro ocupa mais espaço que o card de pets em desktop. A lista mantém a atualização atual e mostra avatar, nome e metadados. O campo `foto` será acrescentado ao retorno `list_GET.xs`; o formato real serializado pelo Xano será verificado antes de mapear a URL para imagem.
- Formatar `data_nasc` apenas para exibição como dd/mm/aaaa quando o valor puder ser interpretado com segurança. Mapear aliases conhecidos de sexo para “Macho” ou “Fêmea” somente na apresentação; preservar texto não reconhecido e os valores originais usados pela integração. O sexo permanece no controle atual durante esta mudança para não presumir opções nem alterar contrato.
- A foto é exibida apenas quando o retorno autenticado fornece um endereço consumível pela interface; caso contrário, usar a patinha. Falhas de cadastro e atualização continuam sendo exibidas pelos estados/mensagens atuais.

### Alternativas consideradas

- Embutir o menu em `profile_view()`: rejeitado porque duplicaria UI e impediria o wrapper reutilizável pedido para as telas seguintes.
- Criar rotas temporárias para as opções sem tela: rejeitado porque produziria destinos falsos e ampliaria o escopo; itens “Em breve” não navegam.
- Reutilizar a classe de estado de autenticação para controlar o menu: rejeitado por misturar navegação com autenticação/pets e tornar a reutilização dependente do módulo de login.
- Manter o endpoint de listagem sem foto: rejeitado porque impediria o avatar real mesmo quando a foto já foi enviada e armazenada; a adição do campo não muda os campos existentes.

## Riscos / Trade-offs

- **A restauração de `rx.LocalStorage` pode causar flicker ou não ser suportada pela versão instalada.** → Persistir somente a expansão desktop, manter o drawer móvel transitório fechado por padrão e validar o comportamento antes de adotar a persistência; estado Reflex continua compartilhado entre rotas.
- **O valor retornado para `foto` pode ser objeto ou URL e pode depender de autorização.** → Verificar a resposta real do endpoint no ambiente de integração; mapear somente a URL válida e preservar a patinha como fallback, sem enfraquecer o acesso autenticado.
- **Ajustes de largura podem produzir overflow entre o drawer, a grade e a lista.** → Usar flex/grid com `min-width: 0` e validar 1920, 1366, 1024, 768 e 390 px, nos estados aberto e fechado.
- **A lista de opções sem rotas poderia parecer quebrada.** → Apresentá-las como “Em breve” e não gerar navegação até que exista destino.

## Plano de migração

1. Estender a resposta autenticada de listagem para incluir a foto existente, sem remover ou renomear propriedades.
2. Atualizar o frontend para tolerar a ausência do novo campo durante deploy parcial e usar a patinha como fallback.
3. Validar cadastro, listagem, upload, logout e telas responsivas com tutor autenticado.
4. Se a resposta da foto causar incompatibilidade, reverter apenas a adição de `foto` no retorno e manter o perfil com fallback; os demais campos e operações permanecem compatíveis.

## Questões em aberto

Nenhuma decisão de produto pendente. A forma concreta do valor `foto` no retorno do Xano é uma verificação técnica da implementação, não uma mudança no contrato definido aqui.
