# Spec Delta

## Purpose

Permitir à clínica cadastrar pets sob sua responsabilidade provisória e administrar sua disponibilidade para adoção.

## ADDED Requirements

### Requirement: Clínica cadastra novo pet para adoção
O sistema SHALL permitir que a clínica autenticada cadastre um novo pet com nome, espécie, raça opcional, sexo, nascimento, peso e foto quando informados. A clínica da sessão SHALL ser a responsável provisória; o cliente SHALL NOT escolher outra clínica ou tutor. Raça informada SHALL pertencer à espécie.

#### Scenario: Cadastro válido
- **WHEN** a clínica envia dados válidos para um novo pet
- **THEN** o backend cria o pet sob responsabilidade da própria clínica e confirma seu cadastro

#### Scenario: Dados inválidos
- **WHEN** faltam dados obrigatórios ou a raça não corresponde à espécie
- **THEN** o backend rejeita o cadastro sem criar pet

### Requirement: Clínica controla disponibilidade de seus pets
O sistema SHALL permitir à clínica publicar e retirar da adoção somente pets sob sua responsabilidade atual. A disponibilidade inicial SHALL ser desativada e a publicação SHALL exigir ação explícita. O backend SHALL verificar responsabilidade e disponibilidade em cada operação.

#### Scenario: Publicação
- **WHEN** a clínica publica pet sob sua responsabilidade
- **THEN** o pet elegível aparece na listagem de adoção dos tutores

#### Scenario: Pet de outra clínica ou já adotado
- **WHEN** uma clínica tenta alterar disponibilidade de pet pelo qual não é mais responsável
- **THEN** o backend nega a operação e não modifica o pet

### Requirement: Operações administrativas são auditadas
O sistema SHALL registrar de forma protegida a clínica, usuário, pet, ação e instante de cadastro, publicação e retirada. Não SHALL registrar dados clínicos ou credenciais no evento administrativo.

#### Scenario: Publicação auditada
- **WHEN** uma publicação é confirmada
- **THEN** o evento correspondente fica registrado com o responsável e o instante

#### Scenario: Falha de auditoria
- **WHEN** o registro obrigatório de auditoria falha
- **THEN** a operação não é confirmada e não deixa mudança parcial
