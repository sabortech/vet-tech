# Spec Delta

## MODIFIED Requirements

### Requirement: Disponibilidade para adoção depende de autorização registrada
Somente pets marcados como disponíveis por operação administrativa confiável no backend SHALL aparecer na adoção. Para pet de tutor, a equipe SHALL confirmar autorização expressa do tutor atual antes de publicar os dados permitidos. Para pet cadastrado sob responsabilidade provisória da clínica, usuário autorizado dessa clínica SHALL poder publicá-lo. A disponibilidade SHALL iniciar desativada e SHALL NOT ser alterável por endpoints comuns de tutor.

#### Scenario: Pet autorizado é disponibilizado
- **GIVEN** a equipe confirmou a autorização do tutor responsável
- **WHEN** marca o pet como disponível no backend
- **THEN** o pet pode aparecer na lista de adoção para tutores autenticados

#### Scenario: Pet não disponibilizado ou sem autorização
- **GIVEN** o pet não está marcado como disponível ou a autorização de divulgação não foi confirmada para pet de tutor
- **WHEN** um tutor solicita a lista de adoção
- **THEN** o pet e seus dados clínicos não são retornados

#### Scenario: Clínica publica seu pet
- **GIVEN** um novo pet está sob responsabilidade provisória da clínica autenticada
- **WHEN** seu usuário autorizado o disponibiliza
- **THEN** ele pode aparecer na lista de adoção para tutores autenticados

## ADDED Requirements

### Requirement: Adoção encerra responsabilidade provisória da clínica
Ao adotar um pet de clínica, a transferência SHALL encerrar o vínculo de responsabilidade provisória da clínica e atribuir o pet ao tutor autenticado na mesma operação consistente, preservando as demais regras existentes de adoção.

#### Scenario: Transferência da clínica
- **GIVEN** o pet disponível está sob responsabilidade provisória de uma clínica
- **WHEN** o tutor conclui a adoção
- **THEN** a responsabilidade da clínica termina e o tutor da sessão passa a ser o único responsável
