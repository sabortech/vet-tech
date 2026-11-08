# Tasks

## 1. Seleção centralizada

- [x] 1.1 Substituir a lista clínica pela tela comum e encaminhar troca/fechamento/abertura para os destinos descritos; verificar regressões de seleção, carregamento e navegação, acrescentando casos de redirecionamento.
- [x] 1.2 Documentar o fluxo em docs/architecture.md e confirmar consistência com a implementação.

## 2. Arte e integração

- [x] 2.1 Integrar arte local indicada pelo tutor e CSS responsivo com contraste por tema; conferir asset e renderização.
- [x] 2.2 Compilar com escrita e verificar a navegação sem pet e após seleção, registrando resultados e limites.


## 3. Wallpaper em tela inteira

- [x] 3.1 Remover moldura e ocupar toda a área principal com a arte por tema; verificar compilação e capturas desktop/mobile.


## 4. Enquadramento central

- [x] 4.1 Centralizar a arte inteira com contain, preservar o fundo sem moldura e remover o excesso de rolagem da mensagem vazia; verificar compilação e capturas nos dois temas.


## 5. Padrão noturno em toda a área

- [x] 5.1 Criar tile de ossinhos/patinhas, estender por trás da arte centralizada e suavizar junção lateral; compilar e verificar no navegador nos dois temas e larguras responsivas.


## 6. Padrão claro em toda a área

- [x] 6.1 Estender o padrão no tema claro reutilizando a composição existente, com cores bege; verificar compilação e navegador em ambos os temas.


## 7. LED da cena

- [x] 7.1 Reutilizar LED verde horário no contorno da cena nos dois temas, acompanhar enquadramento responsivo e verificar animação, compilação e navegação.


## 8. Ações alinhadas em Meus Pets

- [x] 8.1 Alinhar ações em grade responsiva e incorporar seleção e carregamento no botão; compilar e verificar alinhamento, seleção autorizada e temas no navegador.


## 9. Abrir pet no Dashboard

- [x] 9.1 Encaminhar abertura ao Dashboard com setter de escopo existente e manter contexto clínico; verificar eventos, regressões e filtro no navegador ao abrir dois pets diferentes.


## 10. Remodelação do Prontuário

- [x] 10.1 Remodelar hero, foto com borda fina e cinco cartões, incluir foto/nascimento legível na projeção e documentar; verificar testes de seleção, zero/ausência e compilação.
- [x] 10.2 Verificar Prontuário em desktop/mobile e temas claro/escuro, ações e nova apresentação no navegador; registrar capturas.


## 11. Foto correta no Prontuário

- [x] 11.1 Incluir foto no endpoint de detalhes e fallback compatível com campo omitido, condicionado ao mesmo ID autorizado; testar omissão, prioridade do endpoint, remoção e isolamento por pet, compilar e registrar resultado.


## 12. Mascote de braços abertos

- [x] 12.1 Trocar a mascote do hero pelo asset existente de braços abertos, inspecionar o asset e usar contain para preservar corpo inteiro; verificar compilação.


## 13. Alinhamento superior

- [x] 13.1 Alinhar toolbar às bordas do hero com mesma largura e margens, uniformizar altura dos botões e verificar compilação.


## 14. Cantos da cena

- [x] 14.1 Arredondar a própria camada da imagem para acompanhar LED, preservando brilho e enquadramento; verificar compilação e capturas responsivas nos dois temas.


## 15. LED verde no Prontuário

- [x] 15.1 Aplicar LED horário à foto, hero e cinco cartões reutilizando perimeter_led; verificar compilação, animação e apresentação responsiva nos dois temas.

- [x] 15.2 Investigar ausência no servidor ativo, comparar CSS/JS por HTTP e módulo gerado; reiniciar apenas frontend mantendo modo/ambiente e confirmar referências dos LEDs no módulo servido.


## 16. Sombra verde dos elementos

- [x] 16.1 Aplicar sombra derivada da cor do LED ao hero, foto e cinco cartões, conferir CSS público servido e registrar verificação.


## 17. Mascote02

- [x] 17.1 Substituir mascote do hero por mascote02.png e verificar asset e compilação.


## 18. Mascote maior sem sombra

- [x] 18.1 Editar asset com remoção da sombra branca e ampliar mascote responsivamente; inspecionar imagem, compilar e verificar capturas dos dois temas.


## 19. Banner de ossinhos

- [x] 19.1 Criar e aplicar estampa vetorial na faixa central do hero nos dois temas; verificar capturas e compilação.


## 20. Fundo original na faixa

- [x] 20.1 Substituir estampa por recorte de fundopets.jpeg e adaptar ao escuro; verificar capturas responsivas e entrega do CSS atualizado.


## 21. Acabamento da aba Vacinas

- [x] 21.1 Organizar cabeçalho e cards específicos de vacina mantendo estrutura simples, dados e ações; compilar e verificar temas, celular, origem e estado vazio no navegador.


## 22. Cabeçalho de Vacinas

- [x] 22.1 Reorganizar título/descrição e grupo pet/atualizar em layout alinhado responsivo; compilar e verificar capturas nos dois temas.


## 23. Cartão de vacina dividido

- [x] 23.1 Dividir card em dados e imagem fundo.jpeg mantendo dados reais e origem; compilar e conferir temas/mobile com ação funcional.


## 24. LED no cartão de vacina

- [x] 24.1 Aplicar LED horário no contorno externo completo e verificar compilação, animação, temas e layout responsivo no navegador.


## 25. Remodelação de Medicamentos

- [x] 25.1 Criar cartão agrupado, cabeçalho alinhado e composição com recorte transparente de tutu.jpeg; compilar e verificar campos reais, origem, temas e celular no navegador.


## 26. Padronização de Medicamentos

- [x] 26.1 Usar cartão dividido/LED de Vacinas com tartaruga no painel interno, preservando grupos de dados e origem; compilar e verificar temas/mobile.


## 27. Fundo de cadastro no painel

- [x] 27.1 Identificar fundo de cadastro e aplicar fundo_mar.jpeg atrás da tartaruga de Medicamentos; inspecionar asset e conferir CSS público.


## 28. Ícone verde

- [x] 28.1 Substituir tons âmbar do ícone principal por tokens verdes em ambos os temas e sincronizar CSS público.


## 29. Sombra verde dos cartões clínicos

- [x] 29.1 Aplicar box-shadow verde aos cartões completos de Vacinas e Medicamentos e sincronizar CSS público.


## 30. Fundos variados por registro

- [x] 30.1 Sortear e memorizar fundos locais por registro/sessão, aplicar painéis de Vacinas/Medicamentos mantendo tartaruga; testar estabilidade, variedade, isolamento, logout e navegador com múltiplos cards.


## 31. Pet selecionado junto à mascote

- [x] 31.1 Adicionar indicador/ação no Dashboard geral, respeitar ausência de seleção e chat e validar filtros, temas, responsividade e compilação.


## 32. Indicador dentro do cartão selecionado

- [x] 32.1 Mover indicador para o cabeçalho do card correto entre nome e mascote em V, remover versão fixa e validar posicionamento, filtros, temas e celular.


## 33. Foto no indicador

- [x] 33.1 Restaurar avatar circular no botão de seleção, inclusive no celular, e compilar.


## 34. Molde do indicador

- [x] 34.1 Arredondar pontas do indicador em meia-lua com border-radius 999 px e sincronizar CSS público.


## 35. Correção da meia-lua

- [x] 35.1 Excluir indicador da regra global de cápsulas e aplicar molde assimétrico; conferir raio calculado no navegador.


## 36. Visibilidade durante leitura de detalhes

- [x] 36.1 Usar contexto explícito do pet próprio para o indicador sem depender do sucesso da leitura de detalhes; testar loading/falha/ID desconhecido/limpeza e compilar.

## 37. Símbolo de vacinação

- [x] 37.22 Ampliar deslocamento da marca expandida para 24 px à esquerda conforme revisão visual; sincronizar CSS e verificar whitespace.

- [x] 37.21 Ajustar a marca expandida 12 px à esquerda conforme revisão visual, preservando posição do botão de três barras e marca recolhida; sincronizar CSS e verificar whitespace.

- [x] 37.20 Substituir pata da marca pela tartaruga em V e centralizar marca/nome; usar três barras nos toggles em todos os estados, preservando rótulos acessíveis, recolhimento e drawer. Compilar e conferir navegador.

- [x] 37.19 Remover a exceção de cantos retos da sidebar no Dashboard e alinhar o fundo escuro atrás das curvas; verificar raio e continuidade do fundo nos dois temas e no drawer móvel.

- [x] 37.18 Estender o fundo estampado ao contêiner atrás da sidebar para eliminar cantos pretos nas telas de seleção, Meus Pets e Configurações; verificar fundo de layout/conteúdo nos dois temas e tamanhos.

- [x] 37.17 Estender o fundo estampado compartilhado a Configurações nos temas claro/escuro, incluindo suas três abas; sincronizar CSS e verificar seletores/whitespace.

- [x] 37.16 Aplicar o mesmo fundo estampado da orientação sem pet às telas Meus Pets e Mudar pet, nos dois temas; preservar layout, cartões e arte lateral e verificar CSS no navegador.

- [x] 37.15 Restaurar exclusivamente o fundo estampado anterior da orientação sem pet, preservando bege nas demais abas; conferir regra de exceção e sincronizar CSS servido.

- [x] 37.14 Padronizar o fundo das abas no tema claro com o bege #efede6 da referência, incluindo Dashboard e áreas clínicas, preservando imagens dos cartões e tema escuro; conferir cores calculadas no navegador.

- [x] 37.13 Mover Configurações para imediatamente depois de Mudar pet na sidebar do tutor, preservando Sair no rodapé e composição veterinária; compilar e atualizar expectativa de ordem.

- [x] 37.12 Remover Novo pet do menu por solicitação do tutor, mantendo cadastro em Meus Pets e Mudar pet/Sair em suas posições; atualizar expectativa do menu e verificar compilação e navegação.

- [x] 37.11 Unificar sidebar do tutor com Novo pet/Mudar pet junto às abas e somente Sair no rodapé em todas as telas; manter cadastro, seleção, guard de Configurações e menu veterinário, e verificar navegação/mobile.

- [x] 37.10 Centralizar vertical e horizontalmente o conjunto de seleção de pet na área disponível, com tartaruga alinhada ao centro no desktop e fluxo natural no celular; sincronizar CSS e verificar whitespace.

- [x] 37.9 Abrir Mudar pet em modo de seleção com somente a lista reutilizada e tartaruga espreitando à esquerda; preservar Meus Pets completo, seleção segura, histórico, loading/vazio/erros e validar navegação responsiva.

- [x] 37.8 Padronizar sombra verde nos cartões fora do Dashboard usando token CSS comum; conferir Meus Pets, Configurações e cartões clínicos, temas e preservação da sombra original do Dashboard.

- [x] 37.7 Aplicar LED verde contido nos cartões de Minha conta, Segurança e Preferências em Configurações; verificar limites, temas, celular e interação sem envio de dados.

- [x] 37.6 Corrigir enquadramento dos LEDs com posicionamento e isolamento explícitos em cada cartão de Meus Pets e halo suave; verificar limites reais de ambos os LEDs contra os cartões nas portas 3000/3001, temas e tamanhos.

- [x] 37.5 Adicionar LED verde horário nos cartões de cadastro e lista de Meus Pets, respeitando curvas, temas, movimento reduzido e cliques; verificar compilação e navegador.

- [x] 37.1 Incluir seringa decorativa centralizada sobre o cenário do cartão de Vacinas, com contraste nos dois temas e ajuste móvel; verificar compilação e apresentação no navegador sem alterar dados ou ações.

- [x] 37.2 Suavizar o disco da seringa de 91% para 70% de opacidade nos dois temas, reduzir borda/sombra e sincronizar CSS servido; verificar diff e valores CSS.

- [x] 37.3 Substituir tartaruga do painel de Medicamentos por cápsula decorativa, reutilizando círculo com 70% de opacidade, contraste e tamanhos responsivos de Vacinas; verificar compilação e navegador sem alterar mascote de Doenças.

- [x] 37.4 Substituir também a tartaruga de Doenças por coração com pulso no mesmo disco com 70% de opacidade; verificar compilação, temas e tamanhos no navegador.
