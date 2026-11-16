# Spec Delta

## MODIFIED Requirements

### Requirement: Cadastro profissional usa a tela compartilhada
O sistema SHALL oferecer cadastro veterinário em `/cadastro` com nome, e-mail, telefone, senha, confirmação, CRMV, UF, uma ou mais especialidades e uma ou mais espécies atendidas. O vínculo com clínica SHALL ser opcional. Dados válidos SHALL criar somente identidade em `veterinario`, sem autenticar automaticamente nem expor senha/hash.

#### Scenario: Cadastro sem clínica
- **WHEN** uma pessoa envia dados profissionais válidos sem clínica
- **THEN** a conta veterinária é criada e a pessoa retorna ao login com confirmação

#### Scenario: Vínculo inválido
- **WHEN** o cadastro informa uma clínica inexistente
- **THEN** o backend rejeita o cadastro sem criar conta parcial

As exigências de senha, confirmação e retorno ao login SHALL aplicar-se ao cadastro convencional. No cadastro Google, o sistema SHALL importar nome e e-mail verificado, dispensar senha e confirmação e exigir telefone, CRMV/UF, especialidades e espécies antes de criar a identidade e abrir sessão. Clínica continua opcional e todas as validações profissionais permanecem.

#### Scenario: Cadastro profissional Google
- **WHEN** a pessoa conclui OAuth e fornece dados profissionais válidos
- **THEN** cria somente identidade veterinária, com vínculo Google, sem exigir senha e abre sessão isolada
