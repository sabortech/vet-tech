# Proposal

## Why

O cadastro apresenta um espaço extra entre CPF e endereço e seu botão Google está desabilitado. Pessoas que já usam Google devem conseguir criar uma conta sem cadastrar senha, preservando todos os dados obrigatórios de cada perfil.

## What Changes

- Uniformizar espaçamento dos campos sem reservar linha vazia para feedback do CPF.
- Ativar “Cadastrar com Google” reutilizando OAuth, com intenção de cadastro distinta do login existente.
- Importar nome e e-mail verificado e solicitar todos os demais dados obrigatórios: Google não fornece CPF, endereço, telefone ou registro profissional.
- Dispensar senha e confirmação exclusivamente na modalidade Google; concluir cadastro e abrir a sessão após validação completa no backend.
- Manter unicidade entre perfis, vínculo por sub e boas-vindas uma única vez para a nova identidade.
- Preservar cadastro e recuperação por senha existentes; contas Google sem senha recebem orientação apropriada nas configurações.

## Capabilities

### New Capabilities

- `google-registration`: cadastro sem senha com identidade Google verificada, conclusão de dados e sessão.

### Modified Capabilities

- `tutor-registration`: distinguir cadastro convencional e Google, mantendo dados pessoais e espaçamento uniforme.
- `veterinarian-identity`: permitir cadastro profissional Google sem senha, mantendo validações e aptidões.

## Impact

Reflex em `pages/cadastro.py`, componentes de autenticação e estado; Xano OAuth, criação de identidades e vínculo Google. O login atual continua sem criar contas. Credenciais opcionais exigem distinguir ausência de senha nos fluxos de autenticação e recuperação. Reutilizar evento de boas-vindas existente. Dados pessoais permanecem internos, sem tokens Google persistidos ou dados sensíveis em logs. Não altera autorização de prontuário nem introduz serviço pago.
