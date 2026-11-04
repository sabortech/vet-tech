# veterinarian-identity Specification

## Purpose

Permitir cadastro e identificação de veterinários, com registro profissional e aptidões declaradas, sem conceder acesso clínico automaticamente.

## Requirements

### Requirement: Cadastro profissional usa a tela compartilhada
O sistema SHALL oferecer cadastro veterinário em `/cadastro` com nome, e-mail, telefone, senha, confirmação, CRMV, UF, uma ou mais especialidades e uma ou mais espécies atendidas. O vínculo com clínica SHALL ser opcional. Dados válidos SHALL criar somente identidade em `veterinario`, sem autenticar automaticamente nem expor senha/hash.

#### Scenario: Cadastro sem clínica
- **WHEN** uma pessoa envia dados profissionais válidos sem clínica
- **THEN** a conta veterinária é criada e a pessoa retorna ao login com confirmação

#### Scenario: Vínculo inválido
- **WHEN** o cadastro informa uma clínica inexistente
- **THEN** o backend rejeita o cadastro sem criar conta parcial

### Requirement: CRMV recebe validação local e unicidade
O sistema SHALL aceitar CRMV de 1 a 20 caracteres ASCII alfanuméricos após remover espaços externos, normalizar letras para maiúsculas e exigir UF brasileira válida. O par CRMV normalizado/UF SHALL ser único. O sistema SHALL NOT consultar serviço externo ou apresentar a validação sintática como comprovação de habilitação profissional.

#### Scenario: Caracteres válidos
- **WHEN** a pessoa informa ` ab123 ` e uma UF válida
- **THEN** o registro é tratado como `AB123` nessa UF sem consulta externa

#### Scenario: Formato inválido
- **WHEN** o CRMV está vazio, excede 20 caracteres ou contém pontuação, espaços internos ou caracteres de controle
- **THEN** o backend rejeita o campo sem criar conta

#### Scenario: Registro repetido
- **WHEN** outro cadastro usa o mesmo par CRMV/UF normalizado, inclusive simultaneamente
- **THEN** somente uma identidade com esse par pode ser criada

### Requirement: Aptidões profissionais usam catálogos
O sistema SHALL permitir múltiplas especialidades e espécies atendidas por veterinário, usando referências a catálogos. O backend SHALL validar existência, remover repetições de vínculos e distinguir espécie de especialidade. Os catálogos necessários ao cadastro SHALL estar disponíveis antes do login sem expor pessoas ou prontuários.

#### Scenario: Seleção múltipla válida
- **WHEN** a pessoa seleciona duas espécies e duas especialidades existentes
- **THEN** os vínculos são persistidos separadamente para a identidade veterinária

#### Scenario: Referência inexistente ou lista vazia
- **WHEN** o cadastro envia aptidão inexistente ou omite todas as espécies ou especialidades
- **THEN** o backend rejeita o cadastro e informa os campos a corrigir

#### Scenario: Catálogo indisponível
- **WHEN** o catálogo não pode ser carregado ou está vazio
- **THEN** a tela informa a indisponibilidade e não inventa opções nem confirma cadastro incompleto

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
