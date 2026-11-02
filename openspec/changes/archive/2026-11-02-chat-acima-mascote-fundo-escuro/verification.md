# Verificação

Build de produção concluído. Chromium em 1440×1000, 1366×768 e 390×844 confirmou painel acima da mascote, limites da viewport, fundo escuro opaco em 48%, tartaruga clicável acima da sobreposição, fechamento por fundo/mascote/Escape/controle e reabertura. Transições e movimento reduzido aprovados; envio acessível e sem erros JavaScript. Sobreposição inserida no mesmo contexto de empilhamento da mascote para preservar o clique. Evidências em evidence/. node --check, OpenSpec estrito e git diff --check aprovados.
