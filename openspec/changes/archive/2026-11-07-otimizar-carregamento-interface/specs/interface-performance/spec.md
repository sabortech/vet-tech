# Spec Delta

## Purpose
Reduzir trabalho e transferência desnecessários no carregamento da interface, preservando fluxos, dados autorizados e apresentação.

## ADDED Requirements

### Requirement: Dashboard evita histórico clínico antecipado
Abrir pet pelo Dashboard SHALL carregar resumo e seleção autorizada sem solicitar o histórico clínico completo ou a lista clínica de consultas antes de entrar nessa área. A primeira entrada clínica SHALL carregar os dados necessários, sem perder seleção, erro, nova tentativa ou proteção de respostas atrasadas.

#### Scenario: Abrir pet e depois Vacinas
- **WHEN** o tutor abre um pet em Meus Pets e acessa o Dashboard
- **THEN** histórico e consultas clínicas não são lidos antecipadamente
- **AND** ao entrar em Vacinas os dados são carregados pelo fluxo clínico existente

### Requirement: Operações independentes evitam esperas sequenciais
Leituras independentes de catálogos SHALL poder ocorrer em paralelo com limite de quatro solicitações e resultados protegidos por sessão/geração. Operações compostas SHALL reutilizar conexão sem compartilhar autenticação ou resultados entre sessões.

#### Scenario: Lista com pets de várias espécies
- **WHEN** são necessários catálogos de raças de várias espécies
- **THEN** até quatro leituras ocorrem simultaneamente e uma falha parcial mantém os pets visíveis sem aceitar resposta de sessão encerrada

### Requirement: Imagens de interface têm versões de entrega menores
A interface SHALL servir versões otimizadas de imagens decorativas, mantendo composição, transparência, legibilidade e apresentação nos dois temas e celular. Fontes originais SHALL permanecer disponíveis e fotos remotas dos pets SHALL continuar intactas.

#### Scenario: Abrir páginas com cenários e mascotes
- **WHEN** o usuário abre Dashboard, cadastro ou áreas clínicas
- **THEN** a interface usa assets menores que os originais sem alterar seus fluxos ou personagens
