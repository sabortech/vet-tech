# Design

Usar dialog.show para permitir interação com a mascote fora do painel. Desktop com margem direita de 184px; celular com painel acima da mascote. Remover bloqueio de rolagem e armadilha de foco exclusivos do modal. Escape fecha quando foco estiver no chat ou mascote. Fechamento inicia cancelamento de resposta e anima por 200ms antes de executar limpeza existente; guarda impede fechamento duplicado. prefers-reduced-motion remove transições. Testar posição, clique real na mascote, fechar por botão/Escape, reabrir, foco, animação e celular.
