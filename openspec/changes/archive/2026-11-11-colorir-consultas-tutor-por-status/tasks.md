## 1. Implementação

- [x] 1.1 Marcar o cartão da lista com o status existente, preservando a condição do rodapé.
- [x] 1.2 Aplicar paletas amarela e vermelha ao cartão, ícones, selo, disco ilustrado, LED e sombra, com seletores locais e contraste nos dois temas; preservar demais estados.

## 2. Verificação

- [x] 2.1 Executar a compilação de verificação Reflex e os testes existentes pertinentes à apresentação de consultas.
- [x] 2.2 Verificar no navegador os três estados nos temas claro/escuro e larguras desktop/celular; conferir cores computadas do LED e sombra, ausência de overflow, ações e movimento reduzido. Usar dados sintéticos e registrar resultados nesta mudança.

## 3. Organização solicitada durante a implementação

- [x] 3.1 Separar data e horário na projeção existente e no cabeçalho do cartão, com títulos, ícones representativos, espaçamento e quebra responsiva, preservando o fuso e explicitando ausências.
- [x] 3.2 Verificar horário local e ausências, além da organização visual nos dois temas e tamanhos de tela.
- [x] 3.3 Centralizar verticalmente os ícones ao lado de data e horário com regra CSS local; verificar seletor, cascata e whitespace.
- [x] 3.4 Ajustar os ícones ao centro dos valores, com títulos acima, e comprovar no navegador diferença de centro inferior a 1 px nos dois temas e tamanhos de tela.
- [x] 3.5 Aplicar a revisão visual: título Consulta: <número> no alto à esquerda, acima do calendário, e ícones junto aos blocos compactos de título/valor; verificar no navegador.

## 4. Identificação do veterinário

- [x] 4.1 Incluir nome do veterinário na leitura autorizada de consultas sem N+1 e preservar a projeção de dados não publicados.
- [x] 4.2 Mostrar nome no cartão ou “Nome não informado”, sem fallback para o ID.
- [x] 4.3 Verificar projeção, fallback, compilação e apresentação com dados sintéticos; registrar dependência de publicação do endpoint.

## 5. Espaçamento da linha

- [x] 5.1 Acrescentar margem de 16 px acima da linha do rodapé somente nos cartões de Consultas; verificar seletor e whitespace.
- [x] 5.2 Sincronizar os assets servidos pela compilação e confirmar no navegador que a linha fica 16 px abaixo dos campos, nos dois temas e tamanhos de tela.

## 6. Situação dos complementos

- [x] 6.1 Projetar estados de acompanhamento a partir das datas e estados registrados, sem inventar doses tomadas.
- [x] 6.2 Mostrar situação de vacinas/medicamentos e aplicar paletas ao cartão, LED e sombra de todos os complementos somente no detalhe.
- [x] 6.3 Testar classificação, compilar, sincronizar os assets e verificar o detalhe no navegador.
