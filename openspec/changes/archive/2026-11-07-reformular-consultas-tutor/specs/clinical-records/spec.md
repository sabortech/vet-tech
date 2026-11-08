# Spec Delta

## ADDED Requirements

### Requirement: Resumo da consulta reúne dados e narrativas em cartão único
Identificação, estado, datas, profissional, motivo, diagnóstico e observações SHALL compor um único cartão, com títulos acima dos valores e separação interna organizada. O painel lateral SHALL usar o fundo sorteado da consulta com símbolo de prancheta em disco translúcido, no padrão dos demais cartões; no celular SHALL ficar abaixo dos dados sem cortar narrativas.

#### Scenario: Ler resumo completo
- **WHEN** o tutor abre o prontuário da consulta
- **THEN** vê metadados e narrativas no mesmo cartão com imagem lateral, preservando conteúdo e ações existentes

### Requirement: Exames e cenários compartilham padrão dos cartões clínicos
Exames SHALL usar o mesmo cartão dividido das abas clínicas, com dados à esquerda, cenário à direita, LED e símbolo de exame em disco translúcido. Os campos de solicitação, realização, estado, resultado, profissional e data legada disponível SHALL permanecer legíveis. Cartões ilustrados de vacinas, medicamentos, doenças, diagnósticos, exames e consultas SHALL sortear entre quatro cenários, incluindo fundinho.jpeg, com escolha estável por sessão/pet/tipo/registro e prioridade a variedade antes de repetir. Atualizar ou reordenar SHALL preservar escolhas existentes; sair da sessão SHALL limpar o mapa.

#### Scenario: Novos cartões e atualização
- **WHEN** novos registros são exibidos e a lista é atualizada ou reordenada
- **THEN** os quatro fundos participam do sorteio e registros anteriores mantêm seu fundo, sem novas chamadas clínicas para decoração

### Requirement: Consultas do tutor têm apresentação clínica padronizada
A lista de Consultas SHALL compartilhar cabeçalho com pet e atualização das abas clínicas. Cartões SHALL mostrar data, status legível, motivo e profissional, com painel decorativo, LED e ícone em disco translúcido. Ausências SHALL permanecer explícitas. A lista SHALL preservar estados vazio, carregando e erro, e a abertura de prontuários permitida pelo fluxo existente.

#### Scenario: Consultar lista
- **WHEN** o tutor abre Consultas do pet selecionado
- **THEN** vê registros legíveis com ícones e títulos acima dos valores e pode abrir somente prontuários disponíveis

### Requirement: Detalhe clínico organiza conteúdo completo sem duplicar origem
O detalhe SHALL apresentar número/status, datas, profissional, motivo, diagnóstico, observações e complementos publicados com títulos acima dos valores, respeitando textos extensos e quebras de linha. Vacinas, Medicamentos e Doenças SHALL usar os mesmos cartões ilustrados de suas abas, com ícones e transparência equivalentes. Diagnósticos pontuais SHALL manter data e observações próprias da consulta, distintos do histórico consolidado. Exames SHALL preservar seus campos em cartão dividido ilustrado no mesmo padrão. Complementos da consulta aberta SHALL NOT oferecer ação que reabre a mesma origem. Retorno à lista, exportação elegível, permissões e auditoria SHALL preservar seus eventos e critérios existentes.

#### Scenario: Ler documento completo
- **WHEN** o tutor abre um prontuário com complementos publicados
- **THEN** encontra os campos existentes agrupados e legíveis, sem botões de origem redundantes, e pode retornar ou exportar quando permitido

#### Scenario: Proteção mantida
- **GIVEN** uma sessão sem propriedade ou autorização exigida
- **WHEN** tenta ler ou exportar a consulta
- **THEN** o backend mantém a negativa e a auditoria aplicável sem exposição adicional pela nova apresentação

### Requirement: Consultas adaptam apresentação ao dispositivo e tema
Lista e detalhe SHALL funcionar nos temas claro/escuro e no celular sem corte de textos, overflow horizontal ou ações inacessíveis. Decoração SHALL NOT interceptar cliques e animações SHALL respeitar movimento reduzido.

#### Scenario: Ler em tela estreita
- **WHEN** a consulta tem textos extensos em tela de 390 px
- **THEN** conteúdo e ações continuam legíveis em uma coluna sem rolagem horizontal
