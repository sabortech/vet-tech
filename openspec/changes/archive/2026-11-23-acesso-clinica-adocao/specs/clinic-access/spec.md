# Spec Delta

## Purpose

Permitir acesso administrativo isolado por clínica à sua área operacional e aos profissionais vinculados.

## ADDED Requirements

### Requirement: Acesso administrativo é provisionado e isolado
O sistema SHALL autenticar usuários administrativos individuais vinculados a uma clínica pela mesma página e formulário de e-mail e senha usados pelos demais perfis, sem seletor de perfil. O provisionamento SHALL ser restrito à equipe da plataforma. O backend SHALL derivar a clínica da sessão ativa e verificar o vínculo e a situação da conta em cada operação.

#### Scenario: Acesso autorizado
- **WHEN** usuário administrativo ativo autentica com credenciais válidas
- **THEN** acessa somente a área da clínica à qual pertence

#### Scenario: Acesso indevido
- **WHEN** conta inativa, usuário sem autenticação ou de outra clínica solicita dados ou operações da clínica
- **THEN** o backend nega o acesso sem revelar dados protegidos

### Requirement: Clínica consulta seus veterinários
O sistema SHALL listar somente veterinários cujo vínculo atual corresponda à clínica autenticada, apresentando nome, CRMV/UF e especialidades disponíveis. SHALL apresentar estados vazio, carregamento e erro.

#### Scenario: Veterinários de outra clínica
- **WHEN** a clínica consulta sua lista de profissionais
- **THEN** veterinários sem vínculo ou vinculados a outras clínicas não são retornados

### Requirement: Acesso administrativo não concede acesso clínico
O perfil de clínica SHALL NOT conceder leitura, edição ou exportação de prontuários nem alterar autorizações veterinárias por si só.

#### Scenario: Tentativa de acesso ao prontuário
- **WHEN** administrador da clínica solicita prontuário usando apenas sua identidade administrativa
- **THEN** o backend nega a operação clínica
