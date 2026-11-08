# Tasks

- [x] Fazer contorno e sombra do Dashboard individual seguirem a cor da barra, removendo verde decorativo sem data; preservar ausência explícita com LED apagado e sombra neutra, e validar cinco estados/temas/tamanhos.

- [x] Garantir entrega do CSS atualizado com nova versão da URL e visibilidade explícita do LED individual; validar versão carregada e contorno desenhado após trocar pets sem próxima dose.

- [x] Manter LED visível em todos os pets no escopo individual, inclusive sem próxima dose, usando verde decorativo nesse caso e preservando indicação de ausência; verificar cinco pets no navegador.

- [x] Unificar o Dashboard individual de todos os pets em um único cartão com seções internas e LED de status; preservar informações/ações e verificar dois pets, temas e responsividade.

- [x] Vincular cor e halo do contorno animado ao mesmo token de status da barra de cada pet, com precedência sobre estilos genéricos; verificar verde/amarelo/âmbar/vermelho/apagado nos dois temas e preservar movimento reduzido.

## 1. Card completo da listagem

- [x] 1.1 Confirmar as três skills Reflex disponíveis e ler `reflex-docs`; remodelar `_overview_pet` com foto retangular, identificação e três indicadores usando as projeções existentes. Verificar renderização com dados completos, nome longo e campos ausentes, incluindo falha da foto.
- [x] 1.2 Acrescentar faixa verde decorativa com tartaruga reutilizada e texto de próxima dose, sem porcentagem ou papel de barra de progresso. Verificar ausência de dose, data futura e data ultrapassada sem conclusões clínicas indevidas.
- [x] 1.3 Incluir acompanhamento detalhado, prévia limitada e próximo evento em todos os cards; manter as quatro ações vinculadas ao pet correto. Verificar com pelo menos três pets e executar a regressão relevante de `tests/unit/test_dashboard.py` para escopo, ações e projeções.

## 2. Fundo e composição responsiva

- [x] 2.1 Aplicar `/fundopets.jpeg` ao contêiner principal e estilos restritos ao Dashboard em `assets/vet_tech.css`. Verificar imagem carregada, estampas visíveis e fundo cobrindo também lista curta, carregamento, erro e estado vazio.
- [x] 2.2 Substituir a pilha de cards por grade adaptada à largura útil, reorganizando conteúdo e botões em telas estreitas. Verificar em 1366, 1440, 768 e 390 px, com sidebar expandida e recolhida, sem sobreposição ou rolagem horizontal.
- [x] 2.3 Adaptar contraste no tema escuro, foco de teclado e decoração acessível; verificar legibilidade e ações com mascote/chat abertos e fechados. Registrar capturas comparativas na pasta `evidence/` da mudança.
- [x] 2.4 Atualizar a descrição do Dashboard em `docs/architecture.md` com o card e fundo implementados; conferir que a documentação descreve a composição final e mantém as regras existentes de autorização e escopo.

## 3. Integração e aceite visual

- [x] 3.1 Compilar a aplicação seguindo `reflex-process-management` e executar as verificações existentes de Dashboard e datas apropriadas ao ambiente; registrar comandos, resultados e limitações em `verification.md`.
- [x] 3.2 Comparar o desktop com o protótipo usando o card da Jessy como padrão de todos os pets; registrar evidências da foto, hierarquia, indicadores, faixa, acompanhamento e botões, além de capturas mobile e tema escuro.
- [x] 3.3 Validar fluxo completo de filtro geral/individual, agendamento, Vacinas, Prontuário, recuperação de erro e cadastro no estado vazio; confirmar que a visão individual e a seleção clínica preservam seu comportamento existente e documentar o resultado em `verification.md`.

## 4. Acabamento da junção com a sidebar

- [x] 4.1 Estender o fundo ilustrado ao contêiner externo do Dashboard para preencher a área exposta pelos cantos arredondados da sidebar; verificar o canto superior nos temas claro e escuro, preservando o raio do menu e o estilo das demais páginas.
- [x] 4.2 Conforme correção solicitada após a captura real, remover o arredondamento da sidebar somente no Dashboard para eliminar o recorte superior e inferior na junção com o papel de parede; conferir o seletor direto e a precedência sobre o raio original.

- [x] 4.3 Diagnosticar a persistência na aplicação ativa: comparar CSS por HTTP, sincronizar a cópia pública antiga e confirmar que localhost:3000 entrega exatamente o asset fonte corrigido.

- [x] 4.4 Aplicar raio zero diretamente no componente da sidebar do Dashboard, versionar o link do CSS no cabeçalho e executar compilação com escrita; confirmar via HTTP que o HTML ativo contém a URL versionada e que o componente compilado contém o raio zero.

- [x] 4.5 Substituir as duas decorações de tartaruga de cada card pela imagem existente `consultation-pdf/mascote-v.png`, conforme solicitação do usuário; verificar asset e referências e compilar a interface com escrita.


## 5. Indicador de prazo da próxima dose

- [x] 5.1 Derivar estado e texto do LED com datas civis, testar limites de hoje/1/7/8 dias, datas ultrapassadas e ausência de dados válidos, preservando a seleção atual de próxima dose.
- [x] 5.2 Transformar a faixa em botão acessível com LED suave, tartaruga em V, nome e data; verificar cores, texto, foco e navegação para Vacinas do pet por teclado e mouse.
- [x] 5.3 Compilar a interface com escrita, executar regressões e verificação em navegador, registrar evidências e atualizar documentação sobre o novo indicador.

- [x] 5.4 Adicionar tooltip à barra com legenda de todas as cores e explicação de datas ultrapassadas, acessível por hover e foco; verificar conteúdo gerado e compilação com escrita.

- [x] 5.5 Destacar os nomes das cinco cores na legenda com negrito e a respectiva cor, usando conteúdo formatado no tooltip; conferir a renderização compilada e preservar hover, foco e conteúdo.

- [x] 5.6 Tornar brancos os parágrafos da legenda somente no tema escuro, preservando os nomes coloridos e o tema claro; verificar seletor restrito, cores dos nomes e compilação com escrita.

- [x] 5.7 Corrigir a superfície da legenda por tema: fundo branco/texto escuro no claro e fundo escuro/texto branco no escuro, com cores de status legíveis em ambos; verificar contraste e compilação.

- [x] 5.8 Excluir a barra de vacina da regra global de botões em pill para respeitar seu raio local de 6 px, aplicado a todos os cards; verificar a exceção e compilar a interface com escrita.


## 6. Responsividade e desempenho do Dashboard

- [x] 6.1 Separar agendamento e leitura em background para não manter o lock da sessão durante HTTP; testar concorrência limitada, troca de escopo, deduplicação e descarte após logout.
- [x] 6.2 Reutilizar conexão HTTP no lote de resumos sem compartilhar credenciais entre sessões; verificar encerramento e isolamento de headers.
- [x] 6.3 Igualar a altura dos cards em cada linha sem truncar conteúdo, mantendo rodapés alinhados; verificar desktop, mobile e nomes longos.
- [x] 6.4 Medir a liberação do evento e a navegação com API lenta, executar regressões e compilação, registrar resultados e limites; restaurar configuração frontend usada pelo servidor ativo após os testes.


## 7. LED no contorno dos cards

- [x] 7.1 Adicionar LED SVG no contorno de todos os cards, em sentido horário e na cor da barra; manter apagado sem data, sem bloquear ações, sem loops JS nem consultas adicionais e com movimento desativado na preferência reduzida.
- [x] 7.2 Compilar com escrita e verificar em navegador cor, animação, preferência reduzida, estados sem data, responsividade e preservação das ações; registrar evidências.

- [x] 7.3 Substituir o contorno pelo mesmo perimeter_led da área médica e manter movimento horário também com movimento reduzido, em velocidade menor, conforme correção explícita do usuário; testar deslocamento real e cor.


## 8. Tempo até os cards aparecerem

- [x] 8.1 Publicar resumos progressivamente, em ordem dos pets, sem esperar o mais lento; verificar primeiro card com outro request bloqueado e manter invalidação por sessão/escopo/propriedade.
- [x] 8.2 Reaproveitar leituras completas por até 15 segundos na mesma sessão, com invalidação por dia/lista de pets/ações clínicas/logout e botão Atualizar que ignora o reaproveitamento; testar expiração e isolamento.
- [x] 8.3 Verificar no navegador apresentação parcial e retorno rápido, executar regressões e compilação com escrita e registrar medidas e limites no OpenSpec.


## 9. Luz percorrendo a barra

- [x] 9.1 Adicionar reflexo luminoso percorrendo a barra de ponta a ponta em loop de ida e volta, preservando a cor do status, a tartaruga e o clique. Não animar o estado apagado; usar movimento mais lento com preferência reduzida. Verificar deslocamento CSS e compilação com escrita.

- [x] 9.2 Corrigir o reflexo para percurso apenas do início ao fim, reiniciando no começo, e usar a cor exata do status sem mistura com branco; atenuar a base para distinguir o segmento e verificar ciclo e compilação.

- [x] 9.3 Exibir “Situação atual: nome da cor” no tooltip de cada card, usando o estado real do indicador e preservando o destaque colorido; verificar os cinco mapeamentos e compilar com escrita.

- [x] 9.4 Adicionar box-shadow bem suave à moldura da foto de todos os cards, na cor do status com baixa opacidade e cinza sem data, sem animar ou alterar dimensões; verificar CSS e compilação com escrita.

- [x] 9.5 Reforçar a sombra da foto para torná-la perceptível mantendo suavidade: contorno a 45% e halo de 12 px a 35%; compilar e confirmar CSS público atualizado.

- [x] 9.6 Tornar forte o brilho da foto conforme solicitação: contorno sólido de 2 px e dois halos na cor do status, sem animação; compilar e confirmar CSS público.


## 10. Cabeçalho semelhante a Consultas

- [x] 10.1 Reorganizar título, descrição e atualização sólida; colocar filtro e agendamento em barra responsiva com superfície por tema.
- [x] 10.2 Compilar com escrita e executar regressões existentes do Dashboard; registrar resultados.
