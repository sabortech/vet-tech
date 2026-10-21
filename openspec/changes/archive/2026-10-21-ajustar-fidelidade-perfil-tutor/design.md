# Design

## Context

Consulte `proposal.md` para a motivação e o escopo. O perfil existente é composto por `profile_view()` e reutiliza `layout_com_menu()`. Os estilos estão centralizados em `assets/vet_tech.css`, mas o formulário combina uma grade com gap de 12 px e um container flex com gap de 16 px; inputs e selects recebem somente altura mínima, e o campo de data tem apenas rótulo acessível, sem identificação visual. A quebra dos cartões depende de media queries da viewport, apesar da largura de conteúdo variar com o estado da sidebar. O mascote é posicionado relativamente à página, com offsets negativos, e o asset atual não é a pose da referência.

## Goals / Non-Goals

**Goals:**

- Aproximar perfil e sidebar da referência com espaçamento, dimensões e alinhamentos previsíveis em ambos os estados do menu.
- Manter controles legíveis e sem overflow quando a largura da área de conteúdo mudar.
- Dar preview local à foto selecionada sem antecipar o envio ao backend.
- Reutilizar tokens e componentes existentes, mantendo os contratos e eventos atuais.

**Non-Goals:**

- Criar telas, rotas, endpoints, campos ou opções de navegação.
- Alterar o contrato, os valores persistidos ou o comportamento de Xano, cadastro, listagem e logout.
- Introduzir dependências externas ou modificar o asset original do mascote.

## Decisions

1. **Manter as composições existentes e ajustar apenas a apresentação.** O perfil permanece na rota atual; `layout_com_menu()` continua sendo a única composição compartilhada da sidebar. Isso evita duplicar navegação ou alterar o fluxo autenticado. A alternativa de criar uma página/layout novo foi descartada por ampliar o escopo e arriscar a integração já validada.

2. **Dar uma única escala de espaçamento ao formulário e dimensões explícitas aos controles.** Manter os placeholders atuais como identificação visível dos campos vazios e aplicar uma grade com gap uniforme de 16 px e altura de 48 px a inputs e triggers de select. O campo “Data de nascimento” terá, dentro da própria caixa, um rótulo compacto visível enquanto estiver vazio, cobrindo visualmente o placeholder nativo sem interceptar cliques. O controle continua sendo `type="date"` ligado ao mesmo `State.pet_birth_date`; o indicador nativo de calendário permanece à direita, com estilo compatível onde suportado. O navegador continua fornecendo o seletor e a validação nativa de data, e o valor permanece no formato `YYYY-MM-DD` esperado pelo estado e enviado sem conversão no campo `data_nasc` ao Xano. Não transformar o campo em texto nem usar troca de tipo no foco: isso exigiria parsing adicional e poderia alterar a validação ou o formato do contrato.

3. **Refluir o perfil pela largura útil, não só pela viewport.** Tornar o container do perfil referência de container queries: manter duas colunas a 1366 px quando a área restante ainda comportar os cartões; empilhar quando sidebar e paddings reduzirem essa área; passar os campos a uma coluna quando o formulário ficar estreito. A alternativa de ampliar apenas breakpoints globais não cobre uma sidebar expandida em janela larga nem um estado recolhido em janela intermediária.

4. **Usar preview exclusivamente local antes do cadastro.** Ao selecionar um arquivo, criar no navegador uma URL temporária de objeto para o preview; revogá-la ao trocar/limpar a seleção e ao desmontar o componente. O evento atual continua enviando a foto ao Xano somente no cadastro. `rx.selected_files()` oferece nomes/caminhos, não uma URL de imagem local; fazer upload antecipado para o servidor Reflex foi descartado para evitar uma segunda transferência e armazenamento intermediário.

5. **Usar a pose existente de `mascote_logo.png` e reservar espaço para ela na coluna direita.** A comparação visual mostrou que `mascote05.png` tem prancheta e `mascote02.png` tem apenas um braço levantado; `mascote_logo.png` corresponde à pose “espiando” com os dois braços levantados e tem canal alpha real. Gerar uma cópia PNG recortada às margens transparentes, sem alterar o original, e confirmar transparência em fundos contrastantes. Envolver cartão e mascote em uma coluna, deixar o mascote abaixo do cartão e alinhá-lo à borda inferior disponível. Ocultá-lo quando a largura útil dessa coluna cair abaixo de aproximadamente 1100 px ou quando a área livre não comportar a imagem sem sobrepor conteúdo. Isso substitui a posição absoluta relativa à página com offsets negativos, que não conhece a altura do cartão nem a coluna dos pets.

6. **Calibrar a sidebar através dos tokens compartilhados.** Manter as larguras existentes de 260 px e 76 px, ajustar marca, área de interação dos itens e raio externo à referência e preservar o rail/drawer. Patinha e texto continuarão usando o mesmo token de cor. Valores de placeholder/controles que hoje estão duplicados na configuração inline da aplicação serão centralizados nos tokens CSS; estilos específicos de componentes serão aplicados com seletores de classe estreitos.

## Risks / Trade-offs

- **Estilos do tema ou do upload ainda prevalecerem em elementos internos** → inspecionar a árvore renderizada no navegador e direcionar as regras ao trigger/root efetivo, não compensar com `!important` global.
- **URL temporária sobreviver à troca de arquivo ou ao reset do formulário** → revogar a URL ao trocar/limpar e conferir que o valor não participa do evento nem da requisição ao Xano.
- **URL de foto do pet estar ausente/inacessível nos dados de teste** → validar a lista com uma URL HTTP(S) de fixture e separadamente com o fallback; não relaxar o filtro autenticado ou a validação de URLs.
- **Captura no preview do VS Code não representar a viewport CSS real** → comparar com o navegador integrado em dimensões controladas e registrar largura útil, largura do documento e os estados da sidebar.

## Migration Plan

Não há migração de dados, implantação de API ou mudança de dependências. Aplicar CSS e composição de componentes incrementalmente; em caso de regressão visual ou funcional, reverter somente as alterações desta change. Antes de concluir, executar testes unitários e compilação e comparar no navegador as larguras 1920, 1366, 1024, 768 e 390 px, com sidebar aberta e recolhida/drawer fechado e aberto onde aplicável. A change só será arquivada após validação visual do usuário.

## Calibração e verificação autorizadas em 2026-10-21

A referência original foi fornecida em `evidence/prototype-reference.jpeg`. O
usuário autorizou usar Chromium e inspeção das capturas em substituição à
ferramenta de navegador integrado nas tarefas 1.2, 4.2 e 4.3. Isso mantém os
critérios visuais e funcionais e a necessidade de aprovação antes de arquivar.

A largura medida pelo container `profile` exclui os paddings da página. Seu
limite de empilhamento foi calibrado para menos de 1000 px internos, mantendo
o limite de viewport de aproximadamente 1100 px. Assim, 1366 px com sidebar
de 260 px ainda comportam dois cartões legíveis, como na referência. O
formulário continua adaptando os campos conforme a própria largura. A mascote
se oculta quando as colunas empilham; sua base acompanha o conteúdo se a lista
for maior que a área livre da viewport.
