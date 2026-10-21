# Tasks

## 1. Formulário, campos e upload

- [x] 1.1 Manter placeholders legíveis e dar à data nativa rótulo compacto dentro da caixa vazia, com indicador de calendário à direita, validação e valor enviado `YYYY-MM-DD`; aplicar grade única com gap de 16 px e controles de 48 px e verificar esses critérios no navegador e no payload mockado do cadastro.
- [x] 1.2 Ajustar a área de upload para borda verde tracejada, cantos arredondados e altura de 140–150 px; implementar preview local com descarte seguro da URL temporária e verificar seleção, troca, limpeza e ausência de envio antes do cadastro no navegador. Revalidar visualmente altura, borda e funcionamento no Chromium, com inspeção das capturas conforme autorização do usuário.
- [x] 1.3 Preservar os eventos e campos enviados ao Xano ao integrar o preview no cadastro; executar `python -m unittest tests.unit.test_auth_state` e verificar no navegador o envio com e sem foto.
- [x] 1.4 Corrigir o estado de placeholder dos selects Radix de espécie e raça usando o token de placeholder dos inputs, contraste mínimo 4.5:1, chevron visível e cor escura após seleção; preservar os textos existentes, adicionar aria-label a cada controle e validar vazio, hover, foco e preenchido no navegador.
- [x] 1.5 Corrigir o campo de data de nascimento para controle de 48 px sem artefatos de renderização, alinhado verticalmente e com padding igual aos demais; preservar calendário e o valor enviado `YYYY-MM-DD`, validando vazio, foco e preenchido no navegador.

## 2. Cartões, listagem e mascote

- [x] 2.1 Alinhar topo, títulos e padding dos cartões e uniformizar o alinhamento de avatar, nome e metadados; verificar no navegador com uma URL de foto válida e com o fallback sem foto.

- [x] 2.2 Comparar os assets locais com a referência: confirmar que `mascote05.png` mostra a prancheta e `mascote02.png` apenas um braço levantado; usar a pose de `mascote_logo.png`, com os dois braços erguidos e canal alpha real, recortar apenas as margens transparentes para exibição e confirmar a transparência em fundos contrastantes.
- [x] 2.3 Posicionar a mascote como último elemento flexível da coluna direita, centralizada sob o cartão de pets e alinhada à borda inferior da viewport; manter 200–220 px, `pointer-events: none`, sem sobreposição, e ocultar abaixo de aproximadamente 1100 px ou quando as colunas empilharem. Validar visualmente nas larguras indicadas.

## 3. Sidebar e adaptação responsiva

- [x] 3.1 Calibrar dimensões da marca, itens e estado ativo da sidebar com os tokens existentes, mantendo o mesmo token de cor para patinha e texto; verificar visualmente menu aberto e rail sem alterar estado ou navegação. Corrigir especialmente a patinha minúscula no rail, centralizando-a com aproximadamente 28 px.
- [x] 3.2 Reorganizar cartões e campos conforme a largura útil após a sidebar e resolver conflitos dos estilos Reflex/Radix com seletores específicos; verificar ausência de scroll horizontal em 1920, 1366, 1024, 768 e 390 px, nos estados aplicáveis do menu.
- [x] 3.3 Centralizar cores de placeholder e controles nos tokens CSS, removendo duplicações inline relacionadas ao formulário; verificar por busca que os estilos alterados não introduzem cores soltas nem regras `!important`.
- [x] 3.4 Reduzir o espaço entre o título e os campos para 20–24 px, entre linhas para 16 px e entre upload e botão para 16–20 px; fazer o card ajustar-se ao conteúdo sem altura mínima esticada e confirmar ausência de rolagem vertical desnecessária em 1920×1080.
- [x] 3.5 Corrigir a alternância persistente da sidebar: abrir/fechar nos dois sentidos, reajustar o conteúdo e preservar o estado após recarga e navegação; validar estados aberto/recolhido, item ativo e tooltips no navegador.
- [x] 3.6 No rail recolhido, centralizar cada item e seu ícone no eixo da patinha e do botão, remover padding/gap horizontal e ocultar os rótulos com `display: none`, mantendo tooltips e alinhamento do pill ativo; preservar o alinhamento à esquerda no estado aberto e validar a transição sem salto visual.
- [x] 3.7 Alternar o ícone do controle desktop para `menu` quando recolhido e para um ícone de recolher à esquerda quando aberto; atualizar `aria-label` e `aria-expanded` conforme o estado, sem alterar a posição ou a lógica do botão. Confirmar o nome do ícone disponível na versão instalada do Reflex.

## 4. Verificação integrada

- [x] 4.1 Executar `python -m unittest discover -s tests/unit`, `reflex compile --dry`, `openspec validate ajustar-fidelidade-perfil-tutor --strict` e `git diff --check`; corrigir qualquer falha antes da validação visual.
- [x] 4.2 Como última tarefa, comparar visualmente com a imagem de referência no Chromium, com inspeção das capturas conforme autorização do usuário em 1920, 1366, 1024, 768 e 390 px, com sidebar aberta e recolhida nos tamanhos desktop e drawer móvel nos tamanhos aplicáveis; verificar ausência de scroll horizontal, sobreposição e rolagem vertical desnecessária, estados dos campos, upload, mascote e os fluxos de cadastro, preview e envio, listagem, atualização, foto/fallback e logout. Registrar o resultado por largura e estado; não arquivar antes da aprovação visual do usuário.
- [x] 4.3 Validar no Chromium, com inspeção das capturas conforme autorização do usuário sidebar aberta e recolhida em 1920×1080, 1366×768 e 1024 px: eixo central dos ícones, pill ativo, tooltips, ícone/aria do toggle e transição; validar a mascote centralizada sob o cartão, junto à borda inferior e sem sobreposição onde a largura útil comportar duas colunas. Registrar explicitamente qualquer viewport/estado não verificável; não marcar como verificado sem inspeção visual.
