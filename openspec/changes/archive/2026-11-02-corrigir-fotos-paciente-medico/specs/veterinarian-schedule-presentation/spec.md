# Spec Delta

## ADDED Requirements

### Requirement: Foto consistente em todas as apresentações médicas do paciente
O sistema SHALL exibir a foto cadastrada e autorizada do paciente na agenda, lista de consultas, resumo, atendimento e histórico. Resumo e atendimento SHALL priorizar a foto da leitura clínica atual e aceitar a foto da agenda do mesmo pet como compatibilidade após leitura autorizada bem-sucedida. A patinha SHALL aparecer somente para foto nula/vazia. Foto existente com erro SHALL indicar falha de exibição, sem patinha.

#### Scenario: Foto atual disponível
- **GIVEN** o veterinário tem autorização ativa para o paciente
- **WHEN** abre resumo, atendimento ou histórico e a leitura clínica retorna foto válida
- **THEN** a foto atual é exibida mesmo se a agenda não tiver foto ou tiver uma anterior, preservando autorização e auditoria no backend

#### Scenario: Contrato anterior sem foto
- **GIVEN** a leitura clínica autorizada e auditada foi concluída e omite o campo foto (contrato anterior)
- **WHEN** existe foto válida na agenda autorizada do mesmo paciente na sessão atual
- **THEN** a apresentação usa essa foto e nunca a de outro paciente

#### Scenario: Foto nula no banco
- **WHEN** o banco retorna foto nula/vazia, mesmo havendo foto antiga na agenda
- **THEN** a apresentação usa patinha e mantém dados e ações existentes

#### Scenario: Falha de imagem existente
- **WHEN** existe foto no banco mas seu formato é inválido ou seu carregamento falha
- **THEN** a apresentação informa falha de imagem sem usar patinha

#### Scenario: Falha, revogação e resposta antiga
- **GIVEN** mudou o paciente ou a sessão, ou o backend negou a leitura
- **WHEN** chega resposta antiga ou ocorre falha de autorização
- **THEN** nenhum retrato do contexto anterior é restaurado e a falha permanece explícita

## MODIFIED Requirements

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
- **THEN** o perfil usa patinha somente para foto nula/vazia e indica foto indisponível para imagem existente com erro, sem imagem artificial e sem afetar as demais informações
