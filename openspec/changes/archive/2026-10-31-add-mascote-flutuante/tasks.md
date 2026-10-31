# Tasks

## 1. Composição global e assets

- [x] 1.1 Preparar camadas transparentes alinhadas e fallback; verificar dimensões, alpha, peso e composição visual; registrar procedência em assets/mascote/README.md.
- [x] 1.2 Criar componente sem estado em arquivo próprio e integrar extra_app_wraps, CSS e JS globais; verificar compilação Reflex e presença única no wrapper gerado.

## 2. Animação e interação local

- [x] 2.1 Implementar JS idempotente, lerp, clamp, cache geométrico e parada do RAF; verificar em navegador ausência de loop parado e mensagens de backend por movimento.
- [x] 2.2 Implementar crossfade, respiração, piscadas, glow green/rgb, toque, teclado, reduced-motion e clique público; verificar estados, evento único e fallback em testes de navegador; documentar configuração e uso local.

## 3. Integração e encerramento

- [x] 3.1 Verificar navegação, larguras desktop/mobile, colisões, aba oculta e desempenho; registrar comandos, resultados e limitações em verification.md e executar validação estrita OpenSpec.
- [x] 3.2 Sincronizar especificação principal e confirmar correspondência entre requisitos e implementação para o arquivamento de add-mascote-flutuante, sem incluir chat.

## 4. Correção de fidelidade autorizada

- [x] 4.1 Remover sombra de turtu.png, preservar proporção e salvar idle quadrado transparente; conferir dimensões e composição antes do CSS.
- [x] 4.2 Usar imagem inteira com 160 px/aspect-ratio, sombra CSS, lerp 4 px/4 graus e fallback hover; compilar e verificar navegação, teclado, toque, reduced-motion e parada do RAF.
- [x] 4.3 Cobrir viewport inteira no login e verificar capturas desktop/mobile, outras telas e ausência de faixa inferior.
- [x] 4.4 Atualizar documentação/evidências, sincronizar spec e validar a change revisada para arquivamento.
