## MODIFIED Requirements

### Requirement: Consultas do tutor têm apresentação clínica padronizada
A lista de Consultas SHALL compartilhar cabeçalho com pet e atualização das abas clínicas. Cartões SHALL mostrar data, status legível, motivo e profissional, com painel decorativo, LED e ícone em disco translúcido. Ausências SHALL permanecer explícitas. A lista SHALL preservar estados vazio, carregando e erro, e a abertura de prontuários permitida pelo fluxo existente. Consultas em atendimento SHALL apresentar superfície, borda, destaques, LED e sombra amarela. Consultas agendadas ainda não iniciadas SHALL apresentar esses elementos na paleta vermelha. Finalizadas SHALL preservar integralmente a apresentação verde atual. Os demais estados SHALL manter a apresentação existente. As cores SHALL funcionar nos temas claro e escuro, preservando legibilidade, imagens, responsividade e movimento reduzido.

#### Scenario: Consultar lista
- **WHEN** o tutor abre Consultas do pet selecionado
- **THEN** vê registros legíveis com ícones e títulos acima dos valores e pode abrir somente prontuários disponíveis

#### Scenario: Data e horário organizados
- **WHEN** o tutor visualiza o cabeçalho de uma consulta
- **THEN** data e horário aparecem separados, cada um com título e valor agrupados junto ao ícone representativo (calendário e relógio), com espaçamento compacto e quebra responsiva, respeitando o fuso America/Sao_Paulo e explicitando ausências sem inventar horários

#### Scenario: Identificação da consulta como título
- **WHEN** o tutor visualiza o cartão de uma consulta
- **THEN** encontra o título destacado “Consulta: <número>” no canto superior esquerdo, acima do ícone principal de calendário

#### Scenario: Identificação do veterinário responsável
- **GIVEN** um tutor autenticado proprietário do pet
- **WHEN** consulta a lista autorizada de consultas
- **THEN** o campo Veterinário mostra o nome cadastrado do responsável, ou “Nome não informado” quando ausente, sem usar o ID como nome nem expor outros dados do cadastro profissional ou conteúdo de rascunhos

## ADDED Requirements

### Requirement: Complementos da consulta mostram situação e cores de acompanhamento
No detalhe da consulta, vacinas SHALL distinguir aplicação registrada e previsão de próxima dose; medicamentos SHALL informar período prescrito sem afirmar administração de doses. Exames e doenças SHALL preservar o estado registrado. Cartão, LED e sombra SHALL usar vermelho para ação pendente, amarelo para acompanhamento em curso e verde para realização ou período encerrado, sempre com texto explícito. Dados insuficientes SHALL resultar em situação neutra. A classificação SHALL usar somente dados autorizados e data local, sem novas requisições, mudanças clínicas ou efeitos fora do detalhe.

#### Scenario: Vacina aplicada e próxima dose
- **WHEN** há aplicação válida passada e próxima dose registrada
- **THEN** o cartão identifica a aplicação e informa se a próxima data foi ultrapassada (vermelho), está nos próximos sete dias (amarelo) ou é futura (verde), sem afirmar que uma dose posterior está pendente sem confirmação

#### Scenario: Período de medicamento
- **WHEN** há início e fim válidos na prescrição
- **THEN** mostra A iniciar em vermelho, Dentro do período prescrito em amarelo ou Período prescrito encerrado em verde, sem afirmar que as doses foram tomadas

#### Scenario: Estado registrado e ausência
- **WHEN** o detalhe contém doenças ou exames
- **THEN** doença ativa e exame solicitado usam vermelho, doença em tratamento ou controlada usa amarelo, doença curada e exame realizado usam verde; estados desconhecidos e dados insuficientes usam neutro

#### Scenario: Atendimento em andamento
- **WHEN** uma consulta da lista está em atendimento
- **THEN** seu cartão, destaques, LED e sombra usam amarelo, mantendo o texto Em atendimento e sem disponibilizar conteúdo não publicado

#### Scenario: Consulta ainda não iniciada
- **WHEN** uma consulta da lista está agendada
- **THEN** seu cartão, destaques, LED e sombra usam vermelho, mantendo o texto Agendada e as ações existentes

#### Scenario: Consulta finalizada ou outro estado
- **WHEN** a lista contém uma consulta finalizada, legada ou cancelada
- **THEN** cada uma conserva sua aparência e suas ações anteriores, incluindo o verde atual das finalizadas

#### Scenario: Temas e dispositivos
- **WHEN** o tutor visualiza os cartões nos temas claro e escuro, em desktop ou celular, inclusive com movimento reduzido
- **THEN** as cores correspondem ao status, os textos permanecem legíveis e a decoração não intercepta ações nem provoca rolagem horizontal
