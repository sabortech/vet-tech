## Purpose

Proteger o prontuário por consentimento explícito do dono do pet e registrar as operações veterinárias em histórico de auditoria imutável.

## ADDED Requirements

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
