# record-access-control Specification

## Purpose

Control access to veterinary records through explicit tutor consent and preserve
an auditable history of every sensitive operation on a pet's health information.

## Requirements

### Requirement: Explicit veterinarian authorization

The system SHALL allow a veterinarian to view, edit or export a pet's record
only while an authorization granted by that pet's tutor is active. Only the
responsible tutor SHALL be able to create, maintain or revoke that
authorization.

#### Scenario: Authorized record access

- **GIVEN** the pet's tutor granted an active authorization to the veterinarian
- **WHEN** the veterinarian requests an allowed record operation
- **THEN** the system SHALL permit the operation

#### Scenario: Unauthorized or revoked record access

- **GIVEN** no active authorization exists, or an existing authorization was
  revoked
- **WHEN** the veterinarian requests to view, edit or export the pet's record
- **THEN** the system SHALL deny the operation immediately

#### Scenario: Unauthorized authorization management

- **GIVEN** the requester is not the responsible tutor of the pet
- **WHEN** the requester attempts to create, change or revoke an authorization
- **THEN** the system SHALL deny the operation

### Requirement: Immutable access audit

The system SHALL create an audit record for every veterinarian record view,
edit or export, containing the pet, veterinarian, action and timestamp. Audit
records SHALL NOT be editable or deletable by application users.

#### Scenario: Auditing a successful sensitive operation

- **GIVEN** a veterinarian has an active authorization
- **WHEN** the veterinarian views, edits or exports the pet's record
- **THEN** the system SHALL complete the operation and create exactly one audit
  record describing it

#### Scenario: Auditing a denied operation

- **GIVEN** a veterinarian does not have an active authorization
- **WHEN** the veterinarian attempts a sensitive record operation
- **THEN** the system SHALL deny access and SHALL NOT create a successful-action
  audit record

#### Scenario: Preventing audit tampering

- **GIVEN** an audit record has been created
- **WHEN** any application user attempts to modify or delete it
- **THEN** the system SHALL reject the request and preserve the original record

### Requirement: Agendar concede consentimento prévio informado
O sistema SHALL informar ao tutor, antes da confirmação do agendamento, que o veterinário escolhido terá acesso prévio aos dados básicos e histórico publicado do pet. Confirmar SHALL criar ou ativar autorização desse par pet/veterinário, sem ampliar o acesso a outros pets ou profissionais.

#### Scenario: Consulta prévia ao atendimento
- **GIVEN** o dono confirmou agendamento com a liberação de informações apresentada
- **WHEN** o veterinário escolhido abre o histórico antes do dia agendado
- **THEN** o backend permite leitura dos dados publicados desse pet e registra auditoria

#### Scenario: Agendamento falha
- **GIVEN** a reserva não pode ser concluída
- **WHEN** o pedido falha por conflito ou validação
- **THEN** não cria nova autorização nem reativa uma autorização revogada

### Requirement: Autorização clínica é validada a cada operação
O backend SHALL validar identidade veterinária e consentimento ativo por pet antes de ler ou escrever prontuário. Escrita de consulta SHALL exigir também que seja seu responsável e esteja em atendimento. Perfil, autoria e propriedade enviados pelo cliente SHALL NOT substituir essas verificações.

#### Scenario: Outro veterinário tenta editar
- **GIVEN** um profissional tem autorização para ler o pet, mas não é o responsável pela consulta
- **WHEN** tenta alterar ou finalizar aquele atendimento
- **THEN** o backend nega sem alterar dados

#### Scenario: Token de outro perfil ou ID forjado
- **GIVEN** o cliente usa token de tutor ou modifica perfil e identificadores
- **WHEN** tenta executar operação clínica veterinária
- **THEN** o backend nega acesso sem revelar dados de terceiros

### Requirement: Tutor revoga e reativa acesso sem apagar histórico
O sistema SHALL permitir somente ao dono consultar, revogar e reativar as autorizações do pet. Revogação SHALL impedir novas operações clínicas do veterinário imediatamente, inclusive com atendimento aberto. Finalizar consulta SHALL NOT revogar automaticamente; a autorização permanece até ação explícita do tutor.

#### Scenario: Revogação durante atendimento
- **GIVEN** há consulta em atendimento e o tutor revoga o consentimento
- **WHEN** o veterinário tenta nova leitura, salvamento ou finalização
- **THEN** o backend nega e preserva o rascunho protegido e o histórico já publicado

#### Scenario: Histórico do tutor permanece acessível
- **GIVEN** o tutor revogou a autorização de um profissional
- **WHEN** consulta seus atendimentos finalizados
- **THEN** continua vendo todos os registros publicados anteriormente

### Requirement: Leituras e gravações clínicas geram auditoria imutável
O sistema SHALL auditar leitura clínica autorizada, salvamento e finalização com pet, veterinário, ação, consulta quando aplicável e timestamp. Operação sem auditoria SHALL NOT ser reportada como bem-sucedida. Aplicação SHALL impedir edição ou exclusão dos logs por usuários.

#### Scenario: Leitura autorizada
- **GIVEN** há autorização ativa
- **WHEN** o veterinário consulta o histórico publicado
- **THEN** a operação só conclui com registro de auditoria correspondente

#### Scenario: Operação negada
- **GIVEN** não há autorização ativa
- **WHEN** o veterinário solicita dados clínicos
- **THEN** o sistema nega sem criar registro que afirme acesso clínico bem-sucedido

#### Scenario: Tentativa de apagar log
- **GIVEN** um log já foi registrado
- **WHEN** um usuário tenta alterá-lo ou apagá-lo
- **THEN** o backend rejeita e mantém seu conteúdo

### Requirement: Tutor consulta acessos de seus próprios pets
O sistema SHALL disponibilizar ao dono o histórico de autorizações e acessos do pet com profissional, ação e data/hora. Nenhum tutor SHALL consultar logs ou gerenciar permissões de pet alheio. Informações de agenda sem consentimento ativo SHALL se limitar à reserva, sem histórico clínico.

#### Scenario: Consulta dos próprios acessos
- **GIVEN** o tutor é dono do pet
- **WHEN** abre a área de acessos dentro de Consultas
- **THEN** vê os eventos daquele pet e as ações de revogar ou reativar autorização

#### Scenario: Tutor alheio
- **GIVEN** o solicitante não é dono do pet
- **WHEN** tenta consultar logs ou permissões por ID
- **THEN** o backend nega sem revelar conteúdo ou confirmar existência de dados alheios

### Requirement: Exportação do tutor revalida proprietário e publicação no backend
O backend SHALL validar identidade de tutor autenticada, propriedade atual do pet, vínculo da consulta ao mesmo pet e status explícito finalizada a cada exportação e a cada retry. IDs, perfil, status ou campos clínicos enviados pelo cliente SHALL NOT substituir esses controles. SHALL devolver somente dados autorizados publicados e mínimos para o documento; não SHALL confirmar existência de consulta alheia em mensagens. Esta V1 SHALL NOT habilitar exportação veterinária nem ampliar consentimentos.

#### Scenario: Consulta de terceiro ou ID forjado
- **GIVEN** o solicitante não é dono do pet ou envia consulta de outro pet
- **WHEN** tenta exportar alterando identificadores ou perfil
- **THEN** o backend nega, não devolve dados ou PDF e não gera registro que declare exportação autorizada

#### Scenario: Revalidação no retry
- **GIVEN** houve uma tentativa anteriormente autorizada
- **WHEN** uma repetição chega sem sessão válida, sem propriedade vigente ou com consulta inelegível
- **THEN** o backend nega sem reaproveitar autorização antiga ou expor dados

### Requirement: Exportação autorizada possui auditoria imutável e idempotente
O backend SHALL registrar `exportar_consulta` com pet, consulta, tutor ator e timestamp na trilha imutável existente antes de liberar os dados da exportação. A identificação do veterinário responsável, quando presente, SHALL ser distinta do tutor que executa a ação. Falha da auditoria SHALL impedir liberação de dados e PDF. A auditoria SHALL representar a liberação autorizada para emissão, sem afirmar que o arquivo foi salvo pelo navegador. Repetições da mesma operação SHALL produzir no máximo um registro; nova exportação explícita SHALL ter nova operação. Uma chave de operação SHALL ficar vinculada a ator, pet e consulta, sem permitir reutilização para outro alvo. Usuários SHALL NOT editar ou excluir esses registros.

#### Scenario: Auditoria confirmada
- **GIVEN** a exportação da consulta finalizada é autorizada
- **WHEN** o backend libera os dados para emissão
- **THEN** existe exatamente um registro exportar_consulta associado ao tutor ator, pet, consulta e horário

#### Scenario: Auditoria indisponível
- **GIVEN** as validações de propriedade e publicação passaram
- **WHEN** a gravação da auditoria falha
- **THEN** a operação falha sem liberar dados para exportação ou entregar PDF

#### Scenario: Retry concorrente ou resposta perdida
- **GIVEN** duas solicitações representam a mesma operação do mesmo tutor para a mesma consulta
- **WHEN** chegam simultaneamente ou após perda de resposta
- **THEN** as verificações de acesso são repetidas e há somente um registro de liberação autorizada

#### Scenario: Reutilização de chave para outro alvo
- **GIVEN** uma chave já foi usada para uma consulta
- **WHEN** a mesma chave é enviada para outro pet ou consulta pelo mesmo ator
- **THEN** o backend rejeita a reutilização sem liberar dados de outro alvo

#### Scenario: Tentativa negada e adulteração
- **GIVEN** o acesso foi negado ou um log autorizado já existe
- **WHEN** o cliente tenta declarar sucesso ou alterar/excluir o log
- **THEN** não é criado sucesso falso e o registro existente permanece imutável
