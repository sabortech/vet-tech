# Verificação

O cartão da agenda tinha borda fixa e LED apenas no avatar. Foi adicionado o SVG de perímetro reutilizando o componente e os tokens existentes, sem eventos, consultas ou recarregamentos adicionais.

- Agendada: vermelho `#ff5252`; em atendimento: amarelo `#facc15`; finalizada: verde `#79ed4d`.
- Volta contínua em 8 segundos; 20 segundos com preferência de movimento reduzido.
- Navegador Chromium com dados sintéticos: 24 combinações de status, temas claro/escuro, larguras 1280/390 e preferência de movimento. Deslocamento do segmento e cores confirmados.
- Estados cancelado/desconhecido sem LED externo. Altura dinâmica acompanhada pelo SVG; ação Histórico clicável; sem transbordamento horizontal ou erros JavaScript.
- `reflex compile --dry`: passou.
- `openspec validate corrigir-led-cards-horarios --strict`: passou.

Scripts, capturas e resultados estão em `evidence/`. A verificação visual usa um servidor isolado, sem acessar dados clínicos reais.
