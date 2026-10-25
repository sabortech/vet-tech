## MODIFIED Requirements

### Requirement: Identidade veterinária não concede prontuário
O sistema SHALL disponibilizar área veterinária com entradas Horários e Consultas no menu lateral e entrada no atendimento pela lista Consultas. A identidade profissional isolada SHALL NOT liberar prontuário: leitura clínica exige consentimento ativo do dono e escrita exige também responsabilidade pela consulta. A área SHALL iniciar com contexto limpo, sem herdar pets, formulários ou respostas da sessão anterior.

#### Scenario: Veterinário entra
- **GIVEN** uma conta veterinária válida
- **WHEN** o login termina
- **THEN** a área veterinária exibe menu lateral com Horários e Consultas, sem herdar pets ou dados da última sessão de tutor

#### Scenario: Abrir atendimento por endereço direto
- **GIVEN** um profissional conhece o identificador de uma consulta
- **WHEN** abre diretamente sua tela
- **THEN** o backend valida atribuição e consentimento antes de retornar dados de atendimento

## ADDED Requirements

### Requirement: Menu veterinário separa Horários de Consultas
O sistema SHALL abrir calendário vertical em Horários e lista de próximos atendimentos em Consultas. A seção ativa SHALL ser identificável e acessível por teclado e celular. Começar consulta/Retomar SHALL aparecer em Consultas e levar à tela própria do prontuário, mantendo a identidade do atendimento.

#### Scenario: Alternar as apresentações da agenda
- **WHEN** o profissional navega de Horários para Consultas
- **THEN** sai da visão diária por horário e vê a lista dos próximos atendimentos com as ações de começar ou retomar

### Requirement: Tela clínica mantém orientação e recuperação
O sistema SHALL identificar pet, profissional e estado no atendimento e permitir voltar à agenda ou retomar a última versão salva. SHALL distinguir alterações locais não salvas e pedir confirmação antes de descartá-las. Carregamento, erro e repetição de envio SHALL ter feedback acessível em desktop e celular.

#### Scenario: Sair com alterações locais
- **WHEN** o veterinário tenta voltar à agenda com alterações não salvas
- **THEN** recebe aviso e pode permanecer para salvar ou confirmar o descarte somente das alterações locais

#### Scenario: Falha ao finalizar
- **WHEN** o servidor rejeita o encerramento ou a resposta não permite confirmar sucesso
- **THEN** a tela mantém o atendimento recuperável e consulta seu estado antes de repetir uma operação de resultado incerto
