## Purpose

Permitir cadastro de tutores e veterinários com identidade Google verificada e sem senha local, preservando a integridade dos dados obrigatórios e a separação de perfis.

## ADDED Requirements

### Requirement: Cadastro Google exige identidade verificada e dados completos
O sistema SHALL oferecer “Cadastrar com Google”, importar nome e e-mail verificado e dispensar senha e confirmação. SHALL solicitar telefone e, para tutor, CPF e endereço; para veterinário, CRMV, UF, espécies e especialidades, com clínica opcional. SHALL aplicar as mesmas validações e unicidade do cadastro convencional. O Google SHALL NOT ser apresentado como fornecedor de dados que não disponibiliza. Nenhuma conta ou sessão SHALL ser criada antes de concluir esses dados.

#### Scenario: Dados insuficientes
- **WHEN** o Google retorna nome e e-mail e faltam campos obrigatórios
- **THEN** o formulário solicita os campos restantes sem senha e sem criar conta parcial

#### Scenario: Dados completos de cada perfil
- **WHEN** uma pessoa conclui todos os dados válidos do perfil escolhido
- **THEN** o backend cria somente a identidade desse perfil e abre sessão correspondente sem solicitar senha

### Requirement: Cadastro usa prova temporária e consumo atômico
O backend SHALL validar claims Google, PKCE e state de uso único com validade de dez minutos e intenção de cadastro preservada no servidor. A autorização para completar cadastro SHALL ser opaca, expirar em dez minutos, ser vinculada à tentativa da aba e consumida atomicamente uma única vez junto à criação de identidade, reserva de e-mail e vínculo por sub. E-mail e sub SHALL derivar exclusivamente da prova validada. Perfil escolhido SHALL determinar somente o cadastro validado, sem conceder permissões clínicas. Cancelamento ou expiração SHALL limpar a prova na interface; tokens Google e prova SHALL NOT aparecer em logs ou armazenamento persistente do navegador.

#### Scenario: Prova forjada ou reutilizada
- **GIVEN** uma prova expirada, consumida, desconhecida ou pertencente a outra tentativa
- **WHEN** o cliente tenta concluir cadastro
- **THEN** o backend rejeita sem identidade, vínculo ou sessão novos

#### Scenario: Cadastro concorrente
- **WHEN** duas conclusões disputam prova, e-mail, CPF ou CRMV/UF
- **THEN** no máximo uma identidade completa é criada, sem reservas ou vínculos parciais

### Requirement: Contas existentes conservam identidade e permissões
O sistema SHALL manter login Google atual sem criação de contas. No cadastro Google, identidade já existente ou sub já vinculado SHALL orientar entrada pelo login, sem duplicação, mudança de perfil ou novo evento de boas-vindas. Cadastro novo SHALL emitir somente um evento de boas-vindas do perfil persistido; falha do e-mail SHALL NOT desfazer conta concluída. Sessão SHALL confirmar identidade no endpoint protegido e descartar respostas de sessão encerrada.

#### Scenario: Conta já cadastrada
- **WHEN** o cadastro Google identifica conta existente
- **THEN** orienta login e não cria conta, vínculo conflitante ou boas-vindas adicionais

### Requirement: Conta Google não depende de senha local
O sistema SHALL permitir login Google da nova conta sem senha local. Login por senha sem credencial configurada SHALL falhar genericamente. Recuperação por código verificado SHALL permitir definir a primeira senha com os mesmos limites e proteções existentes, sem desvincular Google. Configurações SHALL orientar quem não possui senha a esse fluxo, sem exigir senha atual inexistente. Contas convencionais SHALL preservar seus fluxos atuais.

#### Scenario: Primeira senha opcional
- **WHEN** uma pessoa com conta Google valida recuperação por e-mail e define senha
- **THEN** pode usar senha e Google para a mesma identidade, sem conta adicional

### Requirement: Campos mantêm espaçamento uniforme
O cadastro SHALL usar a mesma distância entre campos consecutivos nos dois perfis, sem linha vazia para feedback. Mensagens reais SHALL permanecer acessíveis e próximas do campo correspondente em celular e desktop, nos temas claro e escuro.

#### Scenario: CPF sem feedback
- **WHEN** o formulário tutor é exibido sem mensagem de CPF
- **THEN** o espaço entre CPF e endereço é igual ao espaço entre os demais campos
