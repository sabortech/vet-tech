## MODIFIED Requirements

### Requirement: Presença global e assets resilientes
O sistema SHALL mostrar uma única tartaruga flutuante no canto inferior direito em todas as páginas, inclusive após navegação, com tamanho aproximado de 160 px desktop e menor no mobile, offsets de aproximadamente 24 px, safe area e área clicável restrita ao botão. O botão SHALL flutuar sobre a página sem faixa reservada, scrollport próprio, redução da viewport ou deslocamento do conteúdo. O sistema SHALL preservar acesso às ações existentes e oferecer fallback quando assets faltarem.

#### Scenario: Navegar entre páginas
- **WHEN** uma pessoa acessa qualquer rota e navega para outra
- **THEN** uma única mascote permanece disponível no canto inferior direito sem bloquear permanentemente ações existentes

#### Scenario: Imagem indisponível
- **WHEN** uma camada transparente não pode ser carregada
- **THEN** um fallback simples mantém o botão visível e utilizável sem quebrar a página


#### Scenario: Geometria independente da mascote
- **WHEN** a mascote é renderizada ou temporariamente ocultada para comparação
- **THEN** tamanho e posição do conteúdo e altura do documento permanecem iguais
