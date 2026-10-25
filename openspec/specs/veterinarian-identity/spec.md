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
O sistema SHALL disponibilizar área autenticada identificada como veterinária, sem listar pets de tutores ou conceder acesso clínico nesta entrega.

#### Scenario: Veterinário entra
- **GIVEN** uma conta veterinária válida
- **WHEN** o login termina
- **THEN** a área veterinária é exibida sem herdar pets ou dados da última sessão de tutor
