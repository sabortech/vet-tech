# clinical-records Specification

## Purpose

Registrar atendimentos veterinários como dados estruturados por consulta e disponibilizar ao tutor o histórico publicado do pet com datas, autoria e origem.

## Requirements

### Requirement: Consulta mantém identidade e ciclo de atendimento
O sistema SHALL vincular cada consulta a um único pet e veterinário responsável, com estados agendada, em atendimento e finalizada. SHALL distinguir horário agendado, início real, fim real e data clínica. O cliente SHALL NOT trocar pet, autoria ou estado por edição do formulário.

#### Scenario: Identidade do atendimento
- **GIVEN** uma consulta atribuída ao veterinário para o pet A
- **WHEN** o cliente tenta salvar dados com pet B ou outra autoria
- **THEN** o backend rejeita sem alterar o atendimento

### Requirement: Prontuário é preenchido na plataforma
O sistema SHALL oferecer tela própria para motivo, diagnóstico em texto, observações e data do atendimento, com retorno opcional. SHALL salvar esses dados no banco sem exigir PDF, documento ou upload. Para finalizar SHALL exigir data, motivo e diagnóstico não vazios, sem exigir doença catalogada.

#### Scenario: Atendimento sem documento
- **WHEN** o veterinário preenche os campos obrigatórios e não informa arquivo nem doença catalogada
- **THEN** pode finalizar um prontuário válido e legível na plataforma

### Requirement: Rascunho é recuperável e isolado do tutor
O sistema SHALL permitir salvar explicitamente o rascunho e retomá-lo pelo responsável autorizado. Rascunhos e complementos de consultas não finalizadas SHALL NOT aparecer nas leituras do tutor ou no histórico publicado. Alterações concorrentes SHALL detectar versão divergente sem sobrescrever dados silenciosamente.

#### Scenario: Retomar após sair da tela
- **WHEN** o veterinário salva o rascunho e volta ao atendimento depois
- **THEN** recupera a última versão confirmada, com os complementos registrados

#### Scenario: Tutor acompanha antes da finalização
- **WHEN** o tutor consulta o pet enquanto o atendimento está aberto
- **THEN** vê o estado da consulta e o histórico já publicado, sem conteúdo do rascunho

### Requirement: Complementos são opcionais e validados individualmente
O sistema SHALL aceitar consulta sem vacinas, doenças, medicamentos ou exames. Quando um complemento for incluído, SHALL validar seus campos e vínculo com a mesma consulta e pet antes de publicar. Uma linha incompleta SHALL impedir a finalização com indicação do erro, preservando o rascunho.

#### Scenario: Consulta sem complementos
- **WHEN** o veterinário informa somente os dados obrigatórios da consulta
- **THEN** pode finalizá-la sem criar complementos artificiais

#### Scenario: Complemento parcial
- **WHEN** há vacina sem data de aplicação ou medicamento sem frequência
- **THEN** a finalização falha e informa a linha a corrigir sem publicação parcial

### Requirement: Vacinas registram aplicação e próxima dose
O sistema SHALL registrar nome da vacina, data de aplicação, lote, pet, veterinário e consulta de origem. A próxima dose SHALL ser opcional, datada e distinta de uma aplicação realizada. Datas inconsistentes SHALL ser rejeitadas; não SHALL gerar aplicação fictícia para uma dose futura.

#### Scenario: Aplicação com reforço previsto
- **WHEN** o veterinário registra aplicação e data de próxima dose
- **THEN** o tutor vê a aplicação realizada e o reforço previsto como informações distintas

### Requirement: Medicamentos preservam a prescrição legível
O sistema SHALL registrar nome, dose com unidade, frequência, via, tipo, data inicial e término quando aplicável, pet, autoria e consulta. Medicamentos contínuos SHALL permitir término ausente. Tipos SHALL incluir contínuo, vermífugo, antipulgas/carrapatos e outro. Não SHALL inferir cura ou aplicação a partir da prescrição.

#### Scenario: Uso contínuo
- **WHEN** o veterinário informa dose, unidade, frequência, via e início de medicamento contínuo sem término
- **THEN** a prescrição é válida e aparece ao tutor com a indicação de uso contínuo

#### Scenario: Período inválido
- **WHEN** o término informado antecede o início
- **THEN** a prescrição é rejeitada para correção sem alteração do histórico publicado

### Requirement: Doença distingue diagnóstico pontual e condição do pet
O sistema SHALL manter doença como catálogo reutilizável, diagnóstico datado vinculado à consulta e condição individual do pet com estado ativa, em tratamento, curada ou controlada. Evoluções SHALL preservar o diagnóstico anterior e sua autoria sem alterar a condição de outro pet.

#### Scenario: Evoluir condição existente
- **WHEN** uma nova consulta muda uma condição do mesmo pet de ativa para controlada
- **THEN** a seção Doenças apresenta o estado publicado mais recente e permite consultar o histórico das duas consultas

### Requirement: Exames usam dados estruturados sem anexo obrigatório
O sistema SHALL permitir registrar tipo de exame, data da solicitação e estado solicitado ou realizado, com resultado em texto e data de realização quando disponíveis. A solicitação SHALL dispensar arquivo e resultado. Exames desta tela SHALL vincular-se à consulta e ao pet; exames legados avulsos SHALL continuar preservados.

#### Scenario: Solicitar exame complementar
- **WHEN** o veterinário informa tipo e data da solicitação sem resultado
- **THEN** o exame é publicado como solicitado ao finalizar a consulta, sem inventar realização

#### Scenario: Registrar resultado disponível
- **WHEN** o veterinário registra exame realizado com data e resultado em texto durante o atendimento
- **THEN** o tutor consegue ler esses dados dentro da consulta após a finalização

### Requirement: Finalizar publica um conjunto consistente
O sistema SHALL finalizar somente consulta em atendimento do responsável com consentimento ativo e versão válida. SHALL persistir consulta, complementos, evoluções e auditoria de forma atômica, registrar fim real e impedir novas edições. Repetir a finalização SHALL retornar a mesma consulta sem duplicar registros.

#### Scenario: Falha durante publicação
- **WHEN** uma parte da gravação ou auditoria falha
- **THEN** nenhum resultado parcial é publicado e a consulta mantém o rascunho recuperável

#### Scenario: Clique duplo em Terminar consulta
- **WHEN** o mesmo encerramento chega mais de uma vez
- **THEN** existe uma única finalização e somente um conjunto de complementos publicados

### Requirement: Tutor lê a consulta completa e os mesmos registros por seção
O sistema SHALL permitir ao dono do pet ler consultas finalizadas com datas, autoria e conteúdo completo. Vacinas, Medicamentos e Doenças SHALL derivar dos mesmos registros publicados, com referência à consulta de origem. Trocar o pet ou encerrar a sessão SHALL limpar o contexto clínico e descartar respostas antigas.

#### Scenario: Consultar vacina fora do atendimento
- **WHEN** o tutor abre Vacinas depois de finalizar uma consulta de seu pet
- **THEN** vê a mesma aplicação, data e profissional registrados na consulta e pode abrir sua origem

#### Scenario: Troca de pet com resposta pendente
- **WHEN** o tutor troca A por B antes de uma leitura clínica de A terminar
- **THEN** os dados de A são descartados e somente conteúdo autorizado de B pode preencher as seções

### Requirement: Histórico anterior permanece preservado
O sistema SHALL preservar IDs, autoria, campos e referências dos registros clínicos existentes durante a evolução do modelo. Registros legados sem associação comprovável a consulta SHALL NOT receber vínculos, datas ou estados clínicos inventados; lacunas SHALL permanecer identificáveis e separadas do novo fluxo.

#### Scenario: Prescrição antiga sem consulta
- **WHEN** o modelo passa a relacionar novas prescrições a consultas
- **THEN** a prescrição antiga permanece no pet sem ser atribuída a um atendimento por aproximação

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

### Requirement: Aba Doenças compartilha apresentação das abas clínicas
A aba Doenças SHALL apresentar cabeçalho com título, descrição, identificação do pet e ação Atualizar, alinhado a Vacinas e Medicamentos. Cada condição SHALL usar cartão com dados à esquerda, painel decorativo à direita e contorno verde animado no padrão existente. No celular o painel SHALL ficar abaixo dos dados, sem corte de textos nem rolagem horizontal. Os dois temas SHALL manter contraste e leitura; animação reduzida SHALL seguir a preferência já aplicada aos cartões clínicos.

#### Scenario: Ler doença no desktop e no celular
- **WHEN** o tutor abre Doenças de seu pet em tema claro ou escuro
- **THEN** vê cartões padronizados com Vacinas e Medicamentos, com todos os textos legíveis e ação de atualização acessível

### Requirement: Cartão de doença preserva conteúdo publicado e origem
O cartão SHALL mostrar nome, estado registrado em português legível, data de evolução, consulta de origem, veterinário disponível e descrição. SHALL preservar quebras de linha e textos extensos. Ausências SHALL permanecer explícitas, sem atribuir estado clínico, profissional ou consulta fictícios. “Notas recentes” SHALL NOT ser fabricadas a partir da descrição ou de registros não retornados pela fonte atual. A ação de consulta SHALL existir somente quando houver vínculo e SHALL reutilizar a leitura autorizada existente.

#### Scenario: Condição com estado registrado
- **WHEN** a fonte retorna estado em_tratamento, data de evolução, descrição e consulta vinculada
- **THEN** o cartão mostra Em tratamento, a data legível e o conteúdo publicado, permitindo abrir a consulta correta

#### Scenario: Registro incompleto ou anterior
- **WHEN** faltam estado, evolução, veterinário ou consulta
- **THEN** as lacunas permanecem identificáveis e não aparece botão de consulta sem vínculo

#### Scenario: Acesso preservado
- **GIVEN** uma sessão sem propriedade do pet ou autorização profissional exigida
- **WHEN** tenta ler o histórico ou a consulta por ação do cartão
- **THEN** o backend mantém a negativa de acesso e a auditoria aplicável, sem exposição de dados no novo layout

### Requirement: Lista de doenças preserva estados de carregamento e isolamento
A aba SHALL distinguir carregamento, erro com nova tentativa e ausência de doenças publicadas. A padronização SHALL preservar descarte de respostas antigas após troca de pet ou sessão e não SHALL introduzir consultas extras para decoração.

#### Scenario: Lista vazia e falha
- **WHEN** a leitura termina vazia ou falha
- **THEN** a aba apresenta respectivamente orientação de ausência de doenças ou erro com nova tentativa, sem mostrar registros fictícios

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
