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
O sistema SHALL oferecer `Exportar PDF` no detalhe existente de uma consulta do próprio tutor, somente com sessão válida, ID válido e status confirmado `finalizada`. A ação SHALL abrir um painel de prévia; somente `Baixar PDF` no painel SHALL solicitar o download. SHALL reconsultar dados autorizados na exportação, sem usar o cache visual como fonte suficiente. SHALL gerar um único PDF por consulta e manter o usuário no detalhe. Consultas agendadas, em atendimento, canceladas, com estado desconhecido ou legado sem status SHALL NOT ser exportáveis nesta V1; a leitura existente dos legados SHALL permanecer disponível.

#### Scenario: Exportação permitida
- **GIVEN** o tutor autenticado é dono do pet e abriu uma consulta finalizada
- **WHEN** solicita Exportar PDF e confirma Baixar PDF no painel
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

### Requirement: Tartaruga encobre a linha divisória da capa do PDF
A capa do prontuário exportado SHALL apresentar a linha divisória horizontal atrás da tartaruga do canto inferior direito. O trecho sobreposto às partes opacas da mascote SHALL ficar encoberto, preservando a composição, os textos e as dimensões atuais do documento (RF10).

#### Scenario: Linha encontra a mascote
- **WHEN** uma consulta elegível é exportada e sua capa é visualizada
- **THEN** a linha permanece visível à esquerda da tartaruga e desaparece atrás de sua silhueta, sem atravessar a ilustração

#### Scenario: Conteúdo do prontuário preservado
- **WHEN** o documento é gerado com dados sintéticos de consulta e textos extensos
- **THEN** identificação, narrativas, acentos e páginas internas continuam íntegros e legíveis

#### Scenario: Mascote reposicionada para a esquerda
- **WHEN** a capa é gerada após o refinamento solicitado pelo usuário
- **THEN** a extremidade direita da tartaruga fica alinhada à borda direita do papel, mantendo posição vertical e sobreposição à linha divisória

#### Scenario: Mascote ampliada na capa
- **WHEN** a capa é gerada após o pedido de aumento
- **THEN** a tartaruga aparece 20% maior, com proporções preservadas, junto à borda direita e sem encobrir os textos da capa

### Requirement: Veterinário exporta consulta finalizada autorizada
O sistema SHALL oferecer Exportar PDF junto da confirmação de atendimento finalizado e ao reabrir uma consulta finalizada no perfil veterinário. Ambos os acessos SHALL abrir o mesmo painel usado pelo tutor. O backend SHALL exigir sessão profissional válida, consentimento ativo do tutor, correspondência pet/consulta e estado finalizado em cada leitura e exportação. A auditoria SHALL identificar o veterinário ator, o responsável pela consulta, o pet, a consulta, a ação e o horário, sem confundir ator com autor do prontuário (RN01–RN08).

#### Scenario: Finalizar e baixar
- **GIVEN** o veterinário possui autorização ativa para o pet
- **WHEN** finaliza o atendimento com sucesso e seleciona Exportar PDF
- **THEN** vê o painel da consulta publicada e pode baixar após confirmar, sem novo salvamento ou alteração clínica

#### Scenario: Baixar posteriormente
- **GIVEN** o veterinário mantém autorização ativa
- **WHEN** reabre uma consulta finalizada e seleciona Exportar PDF
- **THEN** recebe a mesma experiência de prévia e download disponível após finalizar

#### Scenario: Consentimento revogado
- **GIVEN** o consentimento foi revogado, inclusive depois de abrir a prévia
- **WHEN** o profissional tenta carregar a prévia ou baixar o PDF
- **THEN** o backend nega acesso e a interface limpa a prévia sem entregar documento

### Requirement: Painel de prévia é comum a todos os acessos de exportação de consulta
Toda ação Exportar PDF da consulta SHALL abrir um painel com identificação do pet e consulta, datas, profissional disponível, motivo, diagnóstico, observações e todos os complementos publicados que integrarão o documento. A tartaruga SHALL aparecer espreitando pela lateral do painel, sem cobrir textos ou controles. A prévia SHALL mostrar o próprio PDF com todas as páginas acessíveis por rolagem. O painel SHALL seguir a composição do seletor de data, com a tartaruga espreitando ao lado e o botão Baixar PDF no rodapé inferior; fechar ou cancelar SHALL NOT baixar arquivo. A apresentação SHALL preservar acentos, quebras de linha, campos ausentes explícitos, leitura com textos longos, temas claro/escuro e uso por teclado e no celular sem rolagem horizontal. A prévia SHALL NOT executar marcação clínica nem carregar recursos externos definidos pelo conteúdo.

#### Scenario: Conferir sem baixar
- **WHEN** tutor ou veterinário aciona Exportar PDF por qualquer entrada elegível
- **THEN** vê o painel com a tartaruga lateral e informações completas, sem download automático, exibindo as páginas do PDF gerado na prévia

#### Scenario: Celular e acessibilidade
- **WHEN** o painel é aberto em tela de 390 px, com textos longos ou navegação por teclado
- **THEN** as informações têm rolagem, a tartaruga não obstrui leitura, Baixar PDF fica acessível abaixo do conteúdo e o foco retorna ao acionador ao fechar

### Requirement: Prévia e download mantêm autorização e contexto
A prévia SHALL usar dados consultados e auditados no backend e conter somente registros publicados da consulta selecionada. Baixar PDF SHALL revalidar acesso e auditar a emissão, com idempotência para retries da mesma tentativa e nova operação para outra emissão explícita. A interface SHALL bloquear confirmações duplicadas, apresentar carregamento e falhas seguras, e invalidar a prévia e trabalhos pendentes após fechamento, troca de consulta, pet, rota, perfil ou sessão. Se os dados publicados reconsultados diferirem da prévia, SHALL atualizar o painel e exigir nova confirmação antes do download. PDFs SHALL continuar gerados em memória, sem links públicos ou persistência adicional.

#### Scenario: Prévia auditada e cancelada
- **GIVEN** uma sessão autorizada
- **WHEN** abre e fecha a prévia sem confirmar
- **THEN** há auditoria de visualização, sem auditoria de emissão nem download

#### Scenario: Conteúdo mudou após a conferência
- **WHEN** a leitura autorizada do download difere das informações mostradas na prévia
- **THEN** o painel mostra os dados atualizados e solicita nova confirmação, sem baixar um documento diferente silenciosamente

#### Scenario: Resposta atrasada
- **GIVEN** há leitura ou geração em andamento
- **WHEN** o usuário fecha o painel ou muda pet, consulta, perfil, rota ou sessão
- **THEN** o resultado atrasado não repõe dados nem inicia download no novo contexto

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

### Requirement: Identificação nominal do veterinário
O sistema SHALL apresentar o nome do veterinário em todos os campos do profissional nos registros clínicos, autorizações e PDF, mantendo identificadores apenas para operações internas. Sem nome disponível, SHALL exibir “Nome não informado”.

#### Scenario: Registro autorizado com profissional
- **GIVEN** usuário autorizado a consultar o registro
- **WHEN** consulta seus campos ou exporta PDF
- **THEN** o profissional aparece pelo nome, preservando autorização e auditoria existentes

#### Scenario: Nome ausente
- **WHEN** o vínculo profissional não possui nome disponível
- **THEN** a interface exibe “Nome não informado” sem substituir pelo ID
