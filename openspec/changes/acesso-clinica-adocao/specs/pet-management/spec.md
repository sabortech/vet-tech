# Spec Delta

## ADDED Requirements

### Requirement: Pet tem um único responsável atual
Cada pet SHALL ter exatamente um responsável atual: um tutor ou uma clínica. Pets existentes de tutor SHALL manter seu vínculo. Pets cadastrados para adoção por clínica SHALL permanecer vinculados à clínica até a adoção confirmada.

#### Scenario: Responsabilidade exclusiva
- **WHEN** um pet é criado ou tem responsabilidade transferida
- **THEN** o backend rejeita estados sem responsável ou com tutor e clínica simultaneamente

#### Scenario: Compatibilidade com pets existentes
- **WHEN** a alteração de modelo é aplicada
- **THEN** os pets existentes mantêm seus tutores e continuam acessíveis pelos fluxos autorizados
