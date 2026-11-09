# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
