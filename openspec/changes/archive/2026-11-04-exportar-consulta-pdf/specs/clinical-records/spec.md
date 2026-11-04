## ADDED Requirements

### Requirement: Tutor exporta uma consulta finalizada pelo detalhe existente
O sistema SHALL oferecer `Exportar PDF` no detalhe existente de uma consulta do próprio tutor, somente com sessão válida, ID válido e status confirmado `finalizada`. SHALL reconsultar dados autorizados na exportação, sem usar o cache visual como fonte suficiente. SHALL gerar um único PDF por consulta e manter o usuário no detalhe. Consultas agendadas, em atendimento, canceladas, com estado desconhecido ou legado sem status SHALL NOT ser exportáveis nesta V1; a leitura existente dos legados SHALL permanecer disponível.

#### Scenario: Exportação permitida
- **GIVEN** o tutor autenticado é dono do pet e abriu uma consulta finalizada
- **WHEN** solicita Exportar PDF
- **THEN** recebe um documento correspondente ao ID atual somente após confirmação de acesso e auditoria pelo backend

#### Scenario: Consulta ainda não publicada ou legada
- **GIVEN** uma consulta tem status diferente de finalizada ou não possui status
- **WHEN** o detalhe é exibido ou uma exportação é tentada diretamente
- **THEN** a interface não oferece exportação e o backend nega a tentativa sem expor rascunho, preservando a leitura anteriormente permitida

### Requirement: PDF contém apenas dados publicados da consulta selecionada
O PDF SHALL conter a identificação da consulta, pet, autoria disponível, datas e campos clínicos publicados efetivamente retornados pela fonte autorizada. SHALL incluir vacinas, medicamentos, diagnósticos pontuais e exames somente quando pet e `consulta_id` corresponderem à consulta selecionada. SHALL excluir registros sem vínculo comprovado, rascunhos e condições consolidadas do pet que não constituam diagnóstico daquela consulta. Exames avulsos SHALL continuar no histórico original e não integrar este relatório. Campos ausentes SHALL ser omitidos ou apresentados como `Não informado`, sem fabricar nomes, CRMV, assinatura, clínica, diagnóstico ou prescrição.

#### Scenario: Vínculos de complementos
- **WHEN** o histórico autorizado contém complementos desta consulta, de outra consulta e registros legados sem consulta
- **THEN** o PDF inclui somente os complementos publicados desta consulta e não transforma condição consolidada em diagnóstico pontual

#### Scenario: Campos opcionais ausentes
- **WHEN** não há complementos, identificação profissional adicional ou campos opcionais
- **THEN** o PDF permanece válido, sem None, undefined, dados inventados ou seções clínicas artificiais

### Requirement: Documento VetTech é legível e baixado sem persistência
O documento SHALL ser um PDF válido, A4, com identidade visual VetTech aprovada, margens, cabeçalho e rodapé, paginação e suporte a múltiplas páginas e caracteres portugueses. Texto longo e quebras de linha SHALL permanecer legíveis sem truncamento. SHALL ser baixado como `vettech-consulta-<id>.pdf`, usando ID numérico validado e MIME `application/pdf`. SHALL ser gerado sob demanda em memória sem persistência adicional, links públicos ou armazenamento de PDFs. Conteúdo clínico SHALL ser tratado como texto, sem executar marcação nem carregar recursos externos não confiáveis.

#### Scenario: Conteúdo extenso em português
- **WHEN** a consulta tem textos longos com ç, ã, é, quebras de linha e listas de prescrições
- **THEN** o PDF mantém todos os textos, acentos e paginação legível em A4, com assinatura de arquivo %PDF-

#### Scenario: Conteúdo interpretável como marcação
- **WHEN** um campo contém HTML, caminhos de arquivo ou URL externa
- **THEN** esse conteúdo é apresentado como texto e não provoca execução, leitura de arquivo arbitrário ou requisição externa

#### Scenario: Download isolado
- **WHEN** dois tutores exportam consultas simultaneamente
- **THEN** cada um recebe somente seu documento em memória com nome seguro e não há arquivo compartilhado em pasta pública

### Requirement: Exportação conserva contexto e termina com feedback seguro
A interface SHALL indicar processamento e impedir clique duplicado enquanto uma exportação está pendente. SHALL encerrar o processamento com feedback seguro em falhas de autenticação, acesso, registro inexistente, Xano, auditoria ou renderização, sem baixar arquivo parcial/corrompido. SHALL descartar resultados após troca de pet, consulta, saída do detalhe ou encerramento/mudança de sessão, inclusive durante geração. SHALL preservar os demais fluxos clínicos e não expor conteúdo sensível, credenciais ou detalhes técnicos nas mensagens.

#### Scenario: Contexto mudou com operação pendente
- **GIVEN** o tutor iniciou exportação do pet A
- **WHEN** troca de pet, consulta ou sessão ou sai do detalhe antes de terminar
- **THEN** nenhum download ou feedback clínico de A é disparado no novo contexto

#### Scenario: Clique repetido
- **WHEN** o tutor clica repetidamente durante o processamento
- **THEN** existe uma única operação pendente e no máximo um download é disparado

#### Scenario: Falha tratada
- **WHEN** ocorre 401, negativa de acesso, registro inexistente, timeout, 5xx, erro de auditoria ou falha de geração
- **THEN** nenhum PDF parcial é entregue, o processamento termina e há mensagem compreensível que permite nova tentativa quando aplicável sem revelar dados de terceiros
