# Design

## Context
Ver proposal.md. `tutor_area` mostra `pet_list` para qualquer seção sem contexto; Meus Pets já possui a mesma lista. A seleção existente usa geração para descartar respostas antigas.

## Goals / Non-Goals
Centralizar a lista e orientação sem duplicar estado. Não alterar APIs, seleção automática, Dashboard global ou Configurações.

## Decisions
- Revisão de Mudar pet: redirecionar para `/?selecionar=pet`, com projeção do modo pela query atual. Reutilizar `pet_list` sem formulário e arte `/optimized/espreitando.webp` à esquerda; navegação normal para `/` restaura Meus Pets completo. Evitar flag persistente como fonte do modo para preservar voltar/avançar do navegador e saída pelo menu.
- Usar um componente comum em pets.py com arte local, título, explicação e CTA para `/` (Meus Pets).
- Mostrar o mesmo estado sem contexto em todas as seções; cabeçalho e dados clínicos só aparecem com pet alvo, preservando carregamento e nova tentativa.
- Mudar pet e fechar pet limpam contexto pelos handlers atuais e redirecionam a Meus Pets. Abrir pet em Meus Pets redireciona ao Prontuário enquanto a leitura em background preserva sua proteção por geração.
- Usar `assets/fundpet.jpeg` como fundo de um painel central, com título e ação no espaço superior livre. Criar uma variação noturna em asset separado, preservando composição e personagens; o seletor de tema existente alterna a imagem por CSS. Em celular, ampliar a altura do painel e manter a cena inteira na base, com texto acima.

## Risks / Trade-offs
Redirecionamento durante leitura → manter geração e verificar resposta antiga descartada. Arte gerada pode variar em detalhes → inspecionar a versão noturna e preservar a original.

## Migration Plan
Compilar Reflex com escrita e verificar regressões. Reversão restrita aos trechos desta mudança.


## Ajuste: wallpaper em toda a área principal
Conforme captura e correção do tutor, remover painel limitado a 820 px, borda, sombra e raio. Aplicar arte com cover no contêiner de conteúdo inteiro, sem padding externo, nos dois temas. Manter texto e ação no topo com gradiente discreto para legibilidade e reservar espaço para o menu móvel. Cover pode recortar as laterais da arte conforme proporção da tela.


## Ajuste de enquadramento central
Após avaliação do tutor, substituir cover por contain com posição central: a arte aparece inteira, sem ampliação que recorte a cena. A cor de fundo completa a largura restante sem moldura. No celular alinhar a arte à base para liberar o topo para orientação. Remover gradiente que lavava a ilustração e não renderizar mensagem de status vazia que acrescentava rolagem. Esta decisão substitui o cover anterior.


## Fundo noturno contínuo
Estender ossos e patinhas com tile SVG vetorial local atrás da arte noturna centralizada. Compor a cena em pseudo-elemento sem interações, suavizando apenas as bordas laterais com máscara CSS para integrar a imagem ao padrão repetido. Preservar texto e ações e o modo claro.


## Padrão contínuo também no claro
Reutilizar a composição por camadas no tema claro: tile em bege suave, arte original centralizada e mesma máscara lateral. Tema escuro mantém o tile verde e sua arte.


## LED do contorno da cena
Reutilizar perimeter_led com segmento verde e animação horária existente. Moldura decorativa acompanha o quadrado da arte com contain, e retângulo interno cobre x=5,6–94,4%, y=36,2–90%, contornando a cena nos dois temas. Em celular segue o alinhamento inferior da imagem. Sem interação ou eventos; movimento reduzido usa ciclo mais lento.


## Lista de Meus Pets alinhada
Usar grade com avatar, texto flexível e coluna fixa para botões; em lista estreita mover o botão para linha abaixo dos detalhes. O botão selecionado mostra check e “Pet selecionado”, variante sólida e aria-pressed; seleção só é marcada após autorização existente. Substituir o aviso separado; carregamento fica no próprio botão para não deslocar a grade. Preservar o destino de abertura atual.


## Abrir pet no Dashboard
A escolha explícita em Meus Pets deve executar o evento existente set_dashboard_scope com o pet alvo antes do redirecionamento para /dashboard, preservando a leitura autorizada de detalhes. Reutilizar o setter mantém invalidação por geração, allowlist de pets próprios e carregamento/cache existentes. Esta escolha substitui o destino Prontuário definido anteriormente; filtro manual do Dashboard continua independente.


## Prontuário inspirado na referência do tutor
Remodelar somente Início/Prontuário com ações superiores, hero branco com faixa bege, foto circular (contorno neutro de 1 px e sombra leve), nome/espécie/raça e mascote existente à direita. Cinco cartões de dados com ícones abaixo, em três colunas no desktop e uma no celular. Usar tokens escuros por tema e largura máxima centralizada. Acrescentar foto validada e nascimento legível à projeção autorizada sem alterar chaves brutas ou inferir unidade do peso. Preservar loading, erro e retry. Outras seções e tela sem pet conservam comportamento.


## Foto no Prontuário quando endpoint omite o campo
Inspeção confirmou que pets/{pet_id} não inclui foto na allowlist, embora pets inclua. Acrescentar foto ao output XanoScript e, enquanto a versão publicada omitir a chave, reutilizar a foto validada de known_pet apenas quando seu ID coincide com o pet autorizado. Campo foto explícito (inclusive nulo) é autoritativo e não deve ser substituído por cache. Não publicar backend nesta etapa; fallback frontend resolve com contrato anterior.


## Mascote do Prontuário de braços abertos
Usar o asset existente mascote/mascote_hover.png no hero com object-fit contain, preservando corpo inteiro e braços nos dois temas e tamanhos responsivos.


## Alinhamento das ações do Prontuário
Limitar toolbar à mesma largura de 920 px do cartão de identidade, centralizar com margin-inline auto e neutralizar margens do botão ghost. Botões com altura mínima uniforme e quebra responsiva preservada.


## Cantos reais da cena acompanham o LED
A imagem quadrada anterior preservava quinas visíveis nos armários superiores apesar do SVG arredondado. Compor a cena dentro do próprio retângulo do LED via background dimensionado pelas proporções da arte original (88,8% x 53,8%); aplicar border-radius 20 px à camada da imagem, preservando o SVG externo sem recorte do brilho. Fundo estampado continua independente e arte/LED compartilham coordenadas nos dois temas e mobile.


## LED verde do Prontuário
Reutilizar perimeter_led no hero, na moldura circular da foto e nos cinco cartões de dados. Wrappers relativos mantêm dimensões e curvas (18 px hero, 16 px cards, 50% foto). Segmentos verdes giram no sentido horário por CSS, com ciclo mais lento em movimento reduzido e sem interceptar ações. Ambos os temas mantêm seus tokens de superfície.


## Sombra na cor do LED
Adicionar box-shadow suave ao hero, à moldura circular da foto e aos cinco cards, derivado de var(--vt-led-color) com baixa opacidade. Sombra estática, sem mudar dimensões nem animação do LED, nos dois temas. Sincronizar CSS público para servidor ativo.


## Mascote02 no Prontuário
Substituir a imagem do hero por /mascote02.png conforme escolha do tutor, preservando contain e dimensões responsivas.


## Mascote02 maior e sem sombra branca
Gerar versão transparente sem elipse branca incorporada, preservando personagem, pose e proporções e reduzindo margens vazias. Guardar em asset separado, mantendo original. Aumentar coluna/caixa da mascote no hero, adaptando desktop/tablet/celular sem recortar corpo ou sobrepor nome.


## Banner de ossinhos no hero
Criar tile SVG leve com ossos reutilizando o traço existente, aplicado somente na faixa central atrás de foto, nome e mascote. Superfície bege no claro e verde profundo no escuro; gradiente atenua estampa atrás do nome para leitura. Camada decorativa não intercepta eventos e preserva LEDs, sombras e enquadramento.


## Faixa com o wallpaper existente
Conforme correção do tutor, substituir tile de ossinhos por fundopets.jpeg no pseudo-elemento da faixa. Recorte CSS cover alinhado ao topo preserva textura e pequenos motivos sem distorção, evitando grandes silhuetas na faixa desktop. Tema escuro usa o mesmo overlay verde do Dashboard para manter contraste. Sem gerar outra imagem ou alterar o arquivo original.


## Acabamento da aba Vacinas
Conforme esclarecimento do tutor, preservar cabeçalho e listagem simples, sem banner/foto/mascote/LED adicionais. Criar apresentação específica para record_card de vacinas com nome destacado, ícone de seringa, aplicação/lote/próxima dose em grade, origem e veterinário no rodapé e botão compacto alinhado à direita. Reutilizar dados e evento de origem existentes. Limitar largura a 1120 px e manter tokens por tema; em telas estreitas reorganizar campos e rodapé. Outros tipos de registros permanecem iguais.


## Cabeçalho alinhado de Vacinas
Substituir rótulo Área do tutor e badge solto somente na aba Vacinas por título/descrição à esquerda e grupo de contexto/ação à direita. Chip compacto com foto, rótulo Pet selecionado e nome; Atualizar sólido com ícone e estado disabled existentes. Grade reorganiza em duas linhas no celular com contexto e ação juntos. Sem banner e sem mudanças nos registros.


## Cartão de vacina dividido com imagem
Nova referência substitui o cartão simples: coluna de dados à esquerda e painel decorativo fundo.jpeg à direita (62/38). Cabeçalho da vacina, origem, grade 2x2 com aplicação/veterinário/lote/consulta, próxima dose registrada e ação original. Não reproduzir status de vacinação completa, descrições ou datas simuladas da referência. Em celular, imagem vai abaixo dos dados; tema escuro escurece suavemente a imagem.


## LED no cartão inteiro de vacina
Aplicar perimeter_led verde ao contêiner externo do cartão dividido, incluindo dados e imagem, com raio de 18 px. Overflow externo visível mantém halo; arredondar painel de imagem pelos cantos externos para preservar acabamento. Animação horária CSS e ciclo mais lento com movimento reduzido, sem interceptar ações.


## Medicamentos inspirado na referência
Criar apresentação exclusiva da listagem de Medicamentos: cartão central com ícone de cápsula e nome destacado, grupo de dose/frequência/via/tipo à esquerda, datas e proveniência à direita, ação sólida na base. Reutilizar cards projetados e show_consultation_detail; não inferir status Ativo, inexistente no contrato. Ausência explícita e zero preservados. Compor mascote a partir de tutu.jpeg em recorte transparente separado, sem alterar original; ilustração lateral no desktop e abaixo no celular. Cabeçalho reutiliza composição alinhada de Vacinas com título/descrição próprios. Sem mudar outras seções nem detalhe de consulta.


## Medicamentos padronizado com Vacinas
Conforme correção, usar o mesmo contêiner dividido e LED de Vacinas, com dados agrupados mantidos à esquerda e tartaruga integrada ao painel direito, sem ilustração solta na página. Remover largura restrita de 660 px e altura artificial da composição anterior. Ação de origem segue rodapé compacto e cantos/cores seguem tokens compartilhados. Em celular painel da tartaruga aparece dentro da base de cada cartão.


## Fundo de cadastro atrás da tartaruga
Cadastro usa fundo_mar.jpeg (confirmado em pages/cadastro.py). Aplicar o mesmo asset no painel interno medication-art com cover centralizado, mantendo recorte transparente da tartaruga e raios responsivos.


## Ícone principal de medicamento verde
Usar --vt-green no ícone de cápsula e --vt-icon-bg no fundo em ambos os temas, conforme ajuste solicitado.


## Sombra verde nos cartões de Vacinas e Medicamentos
Aplicar a mesma sombra estática do Prontuário ao contêiner compartilhado vaccine-record-card (também usado por Medicamentos), derivando cor de --vt-led-color e preservando dimensões e animação nos dois temas.


## Fundos variados por registro
Catálogo fechado de cenários locais: fundo.jpeg, fundo02.jpeg e fundo_mar.jpeg. Sortear fundo de cada registro de Vacinas/Medicamentos ao receber histórico autorizado, memorizando por sessão/pet/grupo/ID (ou hash do conteúdo para legado sem ID). Preferir fundos ainda não usados no grupo; repetir somente após esgotar catálogo. Releituras e navegação mantêm escolhas, logout limpa mapa. Campo visual enviado à UI é caminho do catálogo, sem alterar dados clínicos. Aplicar via variável CSS no painel, com overlay por tema; Medicamentos mantém sempre o mesmo recorte de tartaruga.


## Contexto de Meus Pets ao lado da mascote no Dashboard
Na visão Todos os pets, compor botão fixo como irmão do layout (fora do container-type do Dashboard) à esquerda da mascote global. Identificar foto/nome do selected_pet autorizado e rótulo Selecionado em Meus Pets. Clique usa set_dashboard_scope para abrir esse pet sem alterar contexto clínico. Sem seleção, orientar escolha em Meus Pets pelo handler existente. Ocultar na visão individual e durante chat aberto para não cobrir assistente. Posicionar respeitando dimensões desktop/mobile da mascote, safe-area, temas e nomes longos.


## Indicador dentro do cartão do pet selecionado
Mover botão para identidade do único card cujo ID é selected_pet_id na visão geral, entre nome e tartaruga em V. Remover composição flutuante e tratamento de chat, que não se aplicam ao controle dentro do cartão. Sem seleção, nenhum card recebe indicador. Clique mantém ação de filtrar o pet. Indicador compacto usa somente rótulo/nome, sem repetir foto ou chevron, para preservar espaço do título e da mascote. Esta decisão substitui posição ao lado da mascote global.


## Avatar no indicador do pet
Restaurar a foto circular dentro do botão de seleção do card. Mantê-la visível no celular com 20 px, sem voltar à posição flutuante.


## Molde arredondado do indicador
Botão de pet selecionado usa border-radius 999 px, formando pontas semicirculares em meia-lua para combinar com avatar circular e curvas do cartão. Sem mudar conteúdo ou ação.


## Correção do molde em meia-lua
A regra global de botões com !important já forçava cápsula, tornando o ajuste anterior ineficaz. Excluir somente dashboard-selected-pet dessa regra e aplicar raio assimétrico: lateral do avatar semicircular e lateral oposta com 10 px, formando molde em meia-lua visivelmente distinto.


## Indicador durante carregamento ou falha dos detalhes
Não depender somente de selected_pet_id (limpo enquanto detalhes são consultados). Projeção dashboard_context_pet_id usa seleção explícita confirmada ou pet_target_id, sempre exigindo correspondência na lista própria da sessão. Identifica intenção de escolha no card autorizado do resumo sem substituir autorização clínica. Contexto desconhecido ou limpo não produz indicador.
