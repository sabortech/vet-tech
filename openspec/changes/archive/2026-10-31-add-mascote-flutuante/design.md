# Design

## Context

Ver proposal.md. O app registra seis rotas em `vet_tech/vet_tech.py`, incluindo atendimento dinâmico. A arquitetura recomenda componentes compartilhados em `vet_tech/components/`. Reflex instalado: 0.9.11. `App.extra_app_wraps` está presente no código instalado e na documentação oficial: https://reflex.dev/docs/api-reference/app/ . `overlay_component` é legado e não será usado. O app já carrega `preferences.js` pelo head; não há componente inferior direito próprio, mas existe o toaster padrão.

## Goals / Non-Goals

**Goals:** componente persistente, movimento sem backend, isolamento de transformações e baixo custo quando parado.

**Non-Goals:** interface de chat, mensagens, dados clínicos, novas dependências de runtime e alterações nos fluxos existentes.

## Decisions

- Um `extra_app_wraps` inclui o botão e o outlet das páginas no mesmo fragmento. Evita repetição nas rotas e wrappers dependentes de autenticação. CSS e script global são registrados no app.
- Idle usa somente `mascote_idle.png`, validado visualmente antes do CSS. `turtu.png` original mede 372×671 RGBA e contém sombra; o usuário autorizou removê-la e centralizar em canvas quadrado, preservando proporções. Nenhum recorte ou resize com fatores X/Y diferentes.
- Botão HTML nativo; imagem inteira em wrapper de rastreamento com origem nos pés, até 4 px/4 graus. Não usar cabeça/corpo/olhos separados, piscadas ou scaleY de respiração enquanto o asset for único. Crossfade de 150 ms para hover existente; se falhar, idle continua visível com glow/pop.
- Guard `window.__mascoteInit`, um pointermove passivo e RAF com lerp .16. Cache geométrico em resize/scroll; sem leituras no RAF e sem backend. Parada após convergência, em hover/foco/toque, reduced-motion e document.hidden.
- Canvas quadrado: width 160 px, height auto e aspect-ratio 1; imagem width/height 100% e object-fit contain. Mobile 112 px; offsets 24 px mais safe area. Sombra elíptica CSS radial abaixo dos pés, separada do arquivo, animação somente opacity/transform. Green/rgb e pré-carga hover preservados.
- Manter wrapper global e reserva inferior para não cobrir controles. Corrigir o fundo sem reduzir a viewport: html/body/root min-height 100dvh e background-size cover; camada decorativa de login fixa cobre também a faixa inferior. Demais páginas mantêm seus fundos.

## Risks / Trade-offs

- [Deformação incorporada ao bitmap] → preservar proporção na preparação e medir escala uniforme no navegador.
- [Conteúdo sob botão fixo] → reserva de rolagem, tamanho menor mobile e teste de colisões; não mover módulos ou redesenhar telas.
- [Navegação/montagem tardia] → wrapper persistente, guard único e inicialização tolerante ao DOM ainda ausente.
- [Métricas de FPS dependem de hardware] → medir RAF parado, duração e ausência de mensagens de movimento; não prometer desempenho universal.

## Migration Plan

Publicação normal dos assets com a aplicação. Reversão remove o wrapper e os registros CSS/JS; nenhum contrato de dados é alterado. Chat permanece pendente em outra change.
