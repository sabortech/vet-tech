# Spec Delta

## MODIFIED Requirements

### Requirement: A tela de login segue a referência visual aprovada
O sistema SHALL apresentar a tela de login existente com a hierarquia e o estilo visual do protótipo aprovado: um cartão dividido com cantos arredondados, uma área clara para o formulário, uma área com a imagem da mascote Vet Tech, a marca Vet Tech, mensagem de boas-vindas, campos de credenciais, ação primária, divisor, entrada com Google e convite ao cadastro. O fundo da página SHALL manter a imagem de floresta com efeito de desfoque, sem desfocar o conteúdo do cartão ou a imagem do painel lateral.

#### Scenario: Renderização do login em desktop
- **WHEN** uma pessoa acessa a rota de login em uma viewport desktop
- **THEN** o sistema exibe formulário e identidade visual no painel claro e a imagem da mascote Vet Tech no painel adjacente, com proporções, tipografia, cores, espaçamentos e cantos arredondados correspondentes ao protótipo aprovado
- **AND** a imagem de floresta aparece ampliada e desfocada atrás do cartão, sem desfocar seus conteúdos

#### Scenario: Exibição das opções visuais do protótipo
- **WHEN** a tela de login é renderizada
- **THEN** os elementos de lembrar acesso e recuperação de senha são apresentados conforme o protótipo, sem introduzir novas ações nem afirmar que esses fluxos estão disponíveis
- **AND** a entrada com Google mantém a aparência do protótipo e só é acionável quando o login Google estiver habilitado no ambiente
