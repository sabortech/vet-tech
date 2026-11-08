# Dashboard individual em cartão único

## Entrega do CSS e visibilidade explícita
Após relato de persistência, a URL do stylesheet foi versionada como
`dashboard-all-pets-led-20261107` e a visibilidade do SVG individual foi
explicitada. Compilação aprovada em 3,359 segundos e frontends 3000/3001/3002
reiniciados. Roteiro aprovado novamente na porta 3002, verificando a URL
efetivamente carregada, display/opacity, dimensões do traço, animação e cores
em cinco pets e nos dois temas/tamanhos. O navegador do usuário não foi
inspecionado; cache anterior é uma hipótese de entrega, não causa confirmada.

## Correção: contorno visível em todo pet selecionado
A regra que ocultava o LED sem próxima dose ficou restrita à visão geral.
No cartão individual, ausência de data usa verde decorativo, preservando
as mensagens de ausência e sem alterar dados clínicos. O roteiro de navegador
passou novamente com cinco pets e 20 combinações de estado/tema/tamanho,
incluindo LED visível e verde no pet sem próxima dose. Capturas atualizadas.

`_individual_pet` reutiliza um único shell de cartão com perímetro LED e
seções internas para identificação, três indicadores, evento, acompanhamentos,
atividade e ações. Não altera fontes de dados, filtro ou handlers. Todos os
pets usam a mesma composição, com LED conforme a próxima dose e apagado sem data.

Compilação aprovada em 3,244 segundos. 46 testes unitários de Dashboard e
carregamento clínico aprovados (PATH do teste inclui o Node instalado para
a verificação do contrato Xano). `dashboard_individual_browser.py` aprovado
na porta 3002 com cinco pets, um por estado: verifica cartão único, ausência
de cartões independentes internos, três indicadores, seções/ações existentes,
LED correspondente à barra original e ausência de overflow em 1440/390 px,
claro/escuro. 20 capturas; nenhuma exceção JavaScript. Contraste dos botões
outline limitado ao novo cartão foi ajustado. Whitespace validado.

Atualização: LED e box-shadow do cartão individual agora seguem a cor da barra de vacinação. Sem próxima dose, LED apagado e sombra neutra, substituindo o verde decorativo anterior. Compilação aprovada; teste de navegador aprovado com cinco estados em 1440/390 px e temas claro/escuro, verificando também a cor computada da sombra. OpenSpec strict e git diff --check aprovados.
