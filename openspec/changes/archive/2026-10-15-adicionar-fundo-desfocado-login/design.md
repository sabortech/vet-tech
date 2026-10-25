# Design

## Context

Consulte `proposal.md` para a motivação e `specs/login-screen-presentation/spec.md` para o contrato visual atualizado. `login_view()` já usa `assets/fundo02.jpeg` como imagem de fundo do painel direito e ocupa a página inteira com um fundo sólido. A tela de cadastro aplica a mesma composição de imagem repetida entre painel e fundo da página, e o fluxo do formulário de login está ligado ao estado existente.

## Goals / Non-Goals

**Goals:**

- Reutilizar a imagem já presente no painel direito como camada decorativa atrás do cartão.
- Manter a imagem do painel e o conteúdo do cartão sem desfoque, com boa legibilidade e adaptação às telas estreitas.

**Non-Goals:**

- Mudar assets, proporções do cartão, navegação ou elementos do formulário.
- Introduzir novos fluxos de autenticação ou dependências.

## Decisions

### Renderizar uma camada de fundo independente

Adicionar uma camada decorativa cobrindo o container externo do login, usando `fundo02.jpeg`, blur e leve ampliação para evitar bordas vazias causadas pelo filtro. O cartão permanece acima dessa camada e conserva seu painel direito atual sem filtro. Essa composição limita o desfoque ao fundo; aplicar `filter` ao container do cartão também desfocaria os campos e textos.

Alternativa considerada: aplicar blur ao fundo existente do container. Rejeitada porque o filtro afetaria todo o conteúdo descendente, a menos que fosse construído um pseudo-elemento independente.

### Preservar a imagem como apresentação decorativa responsiva

Manter a camada atrás do cartão em toda a área da página e preservar os breakpoints atuais do painel lateral. A camada não recebe eventos e não interfere com o envio do formulário nem com a interação em telas estreitas.

Alternativa considerada: ocultar o fundo em viewports menores junto com o painel lateral. Rejeitada porque o efeito de fundo pode permanecer decorativo sem consumir espaço do formulário.

## Risks / Trade-offs

- **[Risco]** O blur pode deixar bordas descobertas ou afetar a legibilidade se a camada não cobrir corretamente o viewport → **Mitigação:** ampliar a camada além dos limites visíveis e manter o cartão nítido acima dela.
- **[Risco]** Repetir a imagem pode aumentar o custo de renderização em dispositivos modestos → **Mitigação:** reutilizar o asset local já carregado e limitar o efeito a uma única camada.

## Migration Plan

Não há migração, alteração de backend ou dependências. A implementação atualiza apenas a composição visual do login. Para rollback, remover a camada de fundo e restaurar a cor sólida anterior do container.
