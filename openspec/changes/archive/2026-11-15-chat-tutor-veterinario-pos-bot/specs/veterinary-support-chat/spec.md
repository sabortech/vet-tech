# Chat tutor–veterinário

## Purpose

Permitir que o tutor continue com um veterinário o atendimento iniciado pelo bot, por meio de chamado e conversa persistentes vinculados a um pet, com acesso restrito aos participantes.

## ADDED Requirements

### Requirement: Encaminhamento confirmado pelo tutor
O sistema SHALL abrir chamado aguardando atendimento quando o tutor autenticado confirmar o encaminhamento solicitado pelo bot, escolher um pet próprio e consentir com o compartilhamento da conversa de origem com o veterinário que assumir. SHALL preservar o conteúdo confirmado e sua autoria, distinguindo resumo do bot de relato do tutor.

#### Scenario: Continuidade do bot
- **GIVEN** o bot propôs atendimento veterinário em uma conversa do tutor autenticado
- **WHEN** o tutor confirma o pet e o compartilhamento
- **THEN** é criado um chamado com tutor, pet, conversa de origem, motivo e horário, em estado aguardando
- **AND** o contexto compartilhado contém somente as mensagens da conversa confirmada, com eventual resumo identificado como gerado pelo bot

#### Scenario: Sem confirmação ou sem pet
- **WHEN** o tutor cancela o encaminhamento ou não possui pet cadastrado
- **THEN** nenhum chamado é criado e o sistema informa a condição necessária para prosseguir

#### Scenario: Propriedade forjada
- **GIVEN** o solicitante não é dono do pet indicado
- **WHEN** tenta confirmar encaminhamento alterando identificadores
- **THEN** o backend rejeita sem criar chamado ou revelar dados do pet

### Requirement: Encaminhamento não duplica chamado
O sistema SHALL garantir no máximo um chamado por conversa de origem e reutilizar o chamado confirmado em repetições da mesma operação. Uma falha ou resposta perdida SHALL permitir consultar o resultado sem gerar outro chamado.

#### Scenario: Confirmações concorrentes
- **WHEN** duas confirmações da mesma conversa chegam simultaneamente ou o tutor repete após timeout
- **THEN** existe somente um chamado e ambas as tentativas identificam o mesmo resultado autorizado

#### Scenario: Outra conversa após encerramento
- **WHEN** o tutor conversa novamente com o bot e confirma novo encaminhamento
- **THEN** pode existir novo chamado, sem reabrir ou alterar o anterior

### Requirement: Fila com exposição mínima
O sistema SHALL disponibilizar aos veterinários autenticados uma fila compartilhada de chamados aguardando, ordenada por criação. Antes da assunção, SHALL expor somente identificador, horário e estado operacional, sem identidade do tutor, dados clínicos, motivo ou conteúdo das mensagens. A fila SHALL NOT exigir vínculo com clínica ou autorização prévia ao prontuário.

#### Scenario: Veterinário consulta pendências
- **GIVEN** há chamados aguardando
- **WHEN** um veterinário autenticado consulta a fila
- **THEN** recebe somente os metadados operacionais permitidos, do mais antigo ao mais recente

#### Scenario: Fila vazia ou erro
- **WHEN** não existem chamados ou a consulta falha
- **THEN** o sistema diferencia ausência de pendências de indisponibilidade, sem inventar chamados

### Requirement: Assunção exclusiva
O backend SHALL permitir que exatamente um veterinário autenticado assuma cada chamado aguardando e passe seu estado para em atendimento. SHALL identificar ao tutor o profissional responsável por nome e CRMV/UF e liberar somente a ele o contexto compartilhado.

#### Scenario: Dois profissionais assumem ao mesmo tempo
- **WHEN** dois veterinários tentam assumir o mesmo chamado
- **THEN** apenas um se torna responsável e o outro recebe conflito sem conteúdo da conversa

#### Scenario: Falha na assunção
- **WHEN** o sistema não confirma a mudança de responsabilidade
- **THEN** não informa atendimento iniciado nem libera o contexto ao solicitante

### Requirement: Troca persistente de mensagens
O sistema SHALL permitir mensagens textuais entre tutor e veterinário responsável em chamado em atendimento, preservando conteúdo, autoria e horário confirmados pelo servidor em ordem estável. SHALL distinguir envio pendente, confirmado e falho e garantir uma única mensagem por operação repetida. Mensagens humanas SHALL NOT ser enviadas automaticamente ao bot.

#### Scenario: Conversa entre participantes
- **WHEN** o tutor ou o veterinário responsável envia mensagem válida
- **THEN** a mensagem persistida fica disponível para ambos sem exigir recarga completa e identifica corretamente seu autor

#### Scenario: Falha de envio e reconexão
- **WHEN** uma confirmação se perde e o participante tenta enviar novamente a mesma operação
- **THEN** o sistema recupera ou confirma uma única mensagem, sem duplicação nem indicação falsa de sucesso

#### Scenario: Mensagem vazia ou indisponibilidade
- **WHEN** o participante envia texto vazio ou o serviço não consegue persistir a mensagem
- **THEN** o envio é rejeitado ou indicado como falho e nenhuma resposta humana é simulada

### Requirement: Acesso restrito aos participantes
O backend SHALL verificar sessão, perfil e participação em cada leitura, envio ou transição do chamado. Somente o tutor proprietário e o veterinário responsável SHALL acessar contexto e mensagens; demais profissionais SHALL ter apenas a visão mínima da fila. Trocar o pet selecionado na aplicação SHALL NOT alterar o pet de um chamado existente.

#### Scenario: Outro tutor ou veterinário
- **GIVEN** o solicitante não é tutor proprietário nem veterinário responsável
- **WHEN** tenta ler mensagens, enviar ou encerrar usando um identificador conhecido
- **THEN** o backend nega sem revelar conteúdo ou confirmar dados de terceiros

#### Scenario: Sessão expirada
- **GIVEN** uma sessão deixou de ser válida
- **WHEN** chega nova operação ou resposta atrasada
- **THEN** nenhum dado é liberado à sessão inválida e o aplicativo solicita autenticação sem reutilizar conteúdo de outra identidade

### Requirement: Retomada do chamado
O sistema SHALL preservar chamados e mensagens após fechamento, recarga ou logout e permitir retomada pelos mesmos participantes autenticados. Dados locais SHALL ser limpos ao trocar de identidade; a recuperação persistente SHALL revalidar o acesso no backend. Conversas apenas com o bot SHALL manter o histórico temporário existente.

#### Scenario: Reabrir em outro acesso
- **WHEN** o mesmo tutor ou profissional responsável entra novamente e consulta seus chamados
- **THEN** recupera estado e mensagens já confirmados, inclusive chamados encerrados em modo de leitura

#### Scenario: Trocar o pet de contexto
- **WHEN** o tutor muda o pet selecionado e retoma chamado anterior
- **THEN** a conversa continua vinculada ao pet original, identificado sem misturar históricos

### Requirement: Avisos internos do atendimento
O sistema SHALL disponibilizar avisos internos de novo chamado para a fila e, aos participantes, de assunção, nova mensagem e encerramento. Avisos SHALL referenciar eventos persistidos sem repetição para o mesmo destinatário/evento, sem expor texto clínico fora da conversa e sem alterar lembretes clínicos existentes.

#### Scenario: Chamado sem profissional disponível
- **WHEN** o chamado foi criado e nenhum veterinário o assumiu
- **THEN** o tutor vê aguardando atendimento, sem prazo garantido ou indicação falsa de profissional conectado

#### Scenario: Destinatário desconectado
- **WHEN** ocorre assunção, mensagem ou encerramento enquanto o destinatário está fora do aplicativo
- **THEN** o evento permanece consultável ao retornar e não depende de e-mail, WhatsApp ou push externo

### Requirement: Cancelamento e encerramento
O sistema SHALL permitir ao tutor cancelar chamado aguardando e aos participantes encerrar chamado em atendimento, registrando ator, motivo e horário. SHALL permitir orientação final do veterinário e manter o histórico somente leitura após encerramento. Encerramento SHALL NOT declarar cura nem criar registros clínicos automaticamente.

#### Scenario: Cancelamento antes da assunção
- **WHEN** o tutor cancela seu chamado aguardando
- **THEN** ele passa a encerrado com motivo cancelamento e deixa a fila

#### Scenario: Cancelamento concorre com assunção
- **WHEN** o tutor cancela enquanto um veterinário tenta assumir
- **THEN** apenas uma transição válida prevalece e a outra recebe o estado atual, sem liberar contexto se o cancelamento venceu

#### Scenario: Veterinário conclui orientação
- **WHEN** o profissional responsável encerra o atendimento e registra sua orientação final
- **THEN** o tutor recebe a orientação e o estado encerrado, com histórico preservado

#### Scenario: Envio após encerramento
- **WHEN** qualquer participante tenta enviar mensagem para chamado encerrado
- **THEN** o backend rejeita sem reabrir o chamado

### Requirement: Independência do prontuário
O sistema SHALL manter a participação no chat distinta da autorização clínica. Encaminhar, assumir e encerrar SHALL NOT conceder ou revogar acesso ao prontuário. Leitura, edição ou exportação clínica SHALL continuar exigindo consentimento ativo do tutor e auditoria existentes; o chat SHALL NOT incorporar automaticamente dados do prontuário.

#### Scenario: Profissional sem consentimento clínico
- **GIVEN** um veterinário assumiu o chamado mas não tem autorização ativa para o pet
- **WHEN** conversa com o tutor e tenta consultar o prontuário
- **THEN** pode ler as mensagens compartilhadas, mas a leitura clínica é negada sem alterar permissões

#### Scenario: Revogação durante a conversa
- **GIVEN** o tutor revoga autorização clínica durante o chat
- **WHEN** o responsável tenta nova operação de prontuário
- **THEN** o backend nega imediatamente, preservando a conversa entre participantes

#### Scenario: Operação clínica autorizada
- **GIVEN** o veterinário possui consentimento ativo
- **WHEN** lê, edita ou exporta prontuário pelo fluxo clínico existente
- **THEN** o sistema aplica as validações e registra a auditoria clínica exigida sem tratar a mensagem do chat como consulta publicada

### Requirement: Rastreabilidade operacional protegida
O sistema SHALL registrar criação, assunção e encerramento com chamado, ator, ação e horário, impedindo alteração ou exclusão desses eventos pelos usuários. Logs técnicos SHALL NOT conter tokens, segredos ou transcrição integral das mensagens. A trilha operacional SHALL ser distinta da auditoria de acesso ao prontuário.

#### Scenario: Evento confirmado
- **GIVEN** uma transição do chamado foi autorizada
- **WHEN** o sistema confirma a operação
- **THEN** há registro persistente correspondente de ator, ação e horário, sem atribuir ao bot uma decisão do veterinário

#### Scenario: Adulteração de evento
- **GIVEN** existe evento operacional registrado
- **WHEN** um usuário tenta alterá-lo ou apagá-lo
- **THEN** o backend rejeita e preserva o original
