# Spec Delta

## ADDED Requirements

### Requirement: Histórico com cabeçalho de perfil do paciente
O rótulo do cabeçalho SHALL ser “Perfil do pet”. O histórico anterior SHALL apresentar retrato circular em destaque, nome, sexo, nascimento, peso informado e contagens reais de consultas, vacinas, medicamentos, doenças e exames antes das categorias. SHALL adaptar o cabeçalho a celular e aos temas existentes, preservando mascote, dados, rolagem, fechamento, foco, falha/nova tentativa e rascunho.

#### Scenario: Dados autorizados do perfil
- **GIVEN** o médico tem autorização ativa para o pet
- **WHEN** abre o histórico
- **THEN** a leitura é validada e auditada pelo backend e o perfil apresenta somente dados e contagens daquele pet, com foto disponível ou patinha

#### Scenario: Resposta antiga ou acesso revogado
- **GIVEN** a seleção/sessão mudou ou o consentimento foi revogado
- **WHEN** uma leitura falha ou uma resposta antiga chega
- **THEN** nenhum retrato ou dado do pet anterior é restaurado

#### Scenario: Foto ausente ou falha
- **WHEN** não há foto válida ou a imagem não carrega
- **THEN** o perfil usa patinha, sem imagem artificial e sem afetar as demais informações
