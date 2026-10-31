# Design

## Context

O botão global já usa imagem proporcional e não altera layout. Glow atual
é CSS infinito de 2,4 s. A interação local controla hover/foco/toque.

## Goals / Non-Goals

**Goals:** tamanho discretamente menor e duas pulsações suaves seguidas de LED estável.
**Non-Goals:** alterações no login, layout, imagens ou chat.

## Decisions

- Tamanhos 140 px desktop e 96 px mobile; manter aspect-ratio e offsets existentes.
- Animação CSS finita de 4 s, uma execução com forwards. Opacidade em 0/25/50/75/100%
  é 0/.95/.12/.95/.75; dois picos lentos, o segundo assenta em luz constante.
  Transform acompanha sutilmente. Não introduzir timers ou chamadas ao backend.
- Saída remove animação e apaga o glow; nova entrada reinicia. Foco visível e
  pressionamento continuam equivalentes. Hover/foco sobrepostos não reiniciam
  a sequência enquanto uma interação continua ativa.
- Reduced-motion mantém LED estático, sem as piscadas. Aba oculta pausa animação.
- Teste mede curva de opacidade pela Web Animations API, finalização, permanência
  do LED, saída/reentrada, tamanho e regressões de acesso/overlay.

## Risks / Trade-offs

- [Confundir piscar olhos com LED] → animar somente glow, sem mudar bitmap.
- [Acessibilidade] → apenas dois ciclos lentos; reduced-motion sem animação.

## Refinamento de intensidade

A área central do glow estava escondida pelo personagem e o gradiente externo
era muito transparente. Ampliar o halo para 116% do canvas, aumentar saturação
visual pelo alpha do gradiente e manter opacidade final .95. Preservar raio
suave, duas pulsações de 4 s, transform/opacity e hitbox original; sem blur/filter.

## Reversão da intensidade

O usuário solicitou desfazer somente o reforço. Restaurar gradiente original,
canvas do glow 100%, picos .95, vale .12 e LED constante .75; manter 140/96 px,
as duas pulsações de 4 s e demais comportamentos anteriores.
