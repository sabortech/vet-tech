# Spec Delta

## Purpose

Permitir que clínicas administrem o cadastro e a associação de veterinários à sua equipe.

## ADDED Requirements

### Requirement: Ações distintas para cadastro e vínculo
A área da clínica SHALL oferecer ações separadas para cadastrar um novo veterinário e para vincular um veterinário que já possui conta.

#### Scenario: Escolha da operação
- **WHEN** a clínica acessa sua lista de veterinários
- **THEN** encontra controles distintos para as duas operações

### Requirement: Cadastro profissional pela clínica
O sistema SHALL permitir ao administrador ativo cadastrar uma nova conta veterinária vinculada à sua própria clínica, respeitando as validações e a unicidade da identidade profissional.

#### Scenario: Cadastro válido
- **WHEN** o administrador informa dados profissionais válidos e conclui o cadastro
- **THEN** a conta é criada com a senha provisória fornecida pela clínica e vinculada à clínica da sessão

#### Scenario: Dados duplicados ou inválidos
- **WHEN** os dados profissionais são inválidos ou conflitam com uma identidade existente
- **THEN** o cadastro é recusado e a interface apresenta o erro

### Requirement: Associação apenas de profissional sem clínica
O backend SHALL permitir a associação de conta existente somente se o veterinário não estiver vinculado a nenhuma clínica, verificando essa condição atomicamente.

#### Scenario: Profissional disponível
- **WHEN** o vínculo autorizado é concluído para um profissional sem clínica
- **THEN** ele passa a integrar a clínica da sessão e aparece na lista

#### Scenario: Profissional já vinculado
- **WHEN** uma clínica tenta vincular profissional que já possui clínica
- **THEN** o backend recusa a operação e preserva o vínculo existente

#### Scenario: Solicitações concorrentes
- **WHEN** duas clínicas tentam associar simultaneamente o mesmo profissional sem clínica
- **THEN** no máximo uma associação é concluída e nenhuma sobrescreve a outra

### Requirement: Aceitação do vínculo de conta existente
O sistema SHALL exigir aceitação do veterinário autenticado antes de efetivar o vínculo de uma conta existente.

#### Scenario: Convite pendente
- **WHEN** a clínica solicita o vínculo de uma conta existente
- **THEN** a associação permanece pendente até a aceitação pelo profissional

#### Scenario: Profissional existente aceita
- **WHEN** o veterinário autenticado aceita o convite e continua sem clínica
- **THEN** o sistema efetiva o vínculo com a clínica que enviou o convite

### Requirement: Senha provisória do novo cadastro
O cadastro de uma conta pela clínica SHALL receber uma senha provisória e permitir que o veterinário a altere posteriormente pelo fluxo de configurações existente.

#### Scenario: Alteração da senha provisória
- **WHEN** o veterinário cadastrado pela clínica acessa as configurações de segurança
- **THEN** pode substituir a senha provisória pelo fluxo de alteração de senha

### Requirement: Autorização administrativa
O backend SHALL validar em cada operação a identidade administrativa ativa e a clínica associada, sem confiar em clínica informada pelo cliente.

#### Scenario: Acesso inválido
- **WHEN** uma conta não autenticada, inativa ou de outro perfil solicita uma operação administrativa
- **THEN** o backend nega a operação

### Requirement: Nenhuma ampliação de acesso clínico
O cadastro ou vínculo SHALL NOT conceder à clínica acesso a prontuários nem modificar autorizações de tutores.

#### Scenario: Acesso clínico após vínculo
- **WHEN** a clínica vincula um veterinário
- **THEN** as regras existentes de autorização e auditoria clínica permanecem em vigor
