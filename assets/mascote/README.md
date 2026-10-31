# Assets da mascote

- `turtu.png`: original enviado pelo usuário, 372×671 RGBA; uma tartaruga com sombra.
- `mascote_idle.png`: versão atual, 320×320 RGBA; uma tartaruga inteira sem sombra.
- `mascote_hover.png`: hover existente, 260×260 RGBA, braços em V.
- `mascote_idle_corpo.png` e `mascote_idle_cabeca.png`: camadas antigas de 260×260,
  mantidas como histórico; não são usadas pelo componente atual.

O usuário autorizou remover a sombra e centralizar a tartaruga em canvas quadrado.
Foi usada a ferramenta integrada de edição de imagens. Prompt: remover somente
sombra oval, manter identidade e proporção larga/simpática, uma tartaruga inteira
centralizada em canvas quadrado transparente, sem glow/texto. Saída 1254×1254;
redução uniforme para 320×320, sem redimensionamento independente de X/Y.

A deformação anterior estava incorporada nas camadas preparadas com fatores de
escala X/Y diferentes; object-fit contain não pode corrigir pixels já deformados.
O idle atual é exibido inteiro, sem cabeça/corpo/SVG sobrepostos. Não incorporar
sombra em futuras imagens: a elipse sob os pés agora é CSS.
