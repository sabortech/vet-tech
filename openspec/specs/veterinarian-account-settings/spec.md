# veterinarian-account-settings Specification

## Purpose
Permitir que o veterinário mantenha os dados permitidos da própria conta, senha e preferências na mesma experiência visual de Configurações do tutor, com isolamento de identidade garantido no servidor.

## Requirements

### Requirement: Configurações médicas reutilizam a experiência existente
O sistema SHALL disponibilizar Configurações em `/configuracoes` para veterinário autenticado, com Minha conta, Segurança e Preferências, mesmo layout, tema, campos e comportamento responsivo do tutor. O menu médico SHALL conter Horários, Consultas e Configurações, identificar a área ativa, permitir retorno às seções e manter logout. Minha conta SHALL apresentar Perfil: Veterinário, nome e telefone editáveis e e-mail e CRMV/UF somente leitura, sem CPF ou endereço fictícios.

#### Scenario: Médico entra em Configurações
- **WHEN** o veterinário abre Configurações pelo menu
- **THEN** vê Minha conta com seus dados e o menu médico, sem destinos exclusivos de tutor

#### Scenario: Preferências compartilhadas
- **WHEN** o veterinário altera tema ou expansão do menu
- **THEN** a preferência é aplicada pelo mecanismo existente em todo o sistema e funciona também no celular

### Requirement: Conta médica usa identidade autenticada e allowlist
O backend SHALL oferecer GET/PATCH veterinario/account autenticados pela tabela veterinario e derivados de auth.id. GET SHALL retornar apenas nome, e-mail, telefone, CRMV e UF. PATCH SHALL aceitar somente nome e telefone obrigatórios após trim, sem modificar e-mail, CRMV, UF, senha, clínica, especialidades, espécies ou identidades fornecidas pelo cliente. Não SHALL retornar hashes ou credenciais. A atualização SHALL validar todos os campos antes de gravar.

#### Scenario: Leitura e atualização próprias
- **GIVEN** um veterinário autenticado
- **WHEN** consulta ou salva nome/telefone válidos
- **THEN** somente sua conta é lida ou atualizada e os campos protegidos permanecem iguais

#### Scenario: Token de outro domínio
- **GIVEN** um token de tutor/user, inválido ou ausente
- **WHEN** solicita conta médica ou troca de senha médica
- **THEN** o backend rejeita sem expor ou alterar dados, inclusive quando IDs numéricos coincidem

#### Scenario: Campos protegidos e valores inválidos
- **GIVEN** um veterinário envia ID de outro usuário, CRMV/e-mail forjados ou campos obrigatórios vazios
- **WHEN** o backend recebe a atualização
- **THEN** somente os campos permitidos da identidade autenticada podem mudar e valores inválidos não causam escrita parcial

### Requirement: Troca de senha médica valida credencial atual
O backend SHALL oferecer POST veterinario/password, verificar senha atual contra o campo senha da conta autenticada, exigir nova senha não vazia e confirmação exatamente igual e armazenar nova senha como hash. SHALL preservar caracteres e política existente, sem retornar ou registrar senhas. Após sucesso a interface SHALL limpar credenciais e sessão atual e conduzir ao login com confirmação.

#### Scenario: Senha atual errada ou confirmação divergente
- **GIVEN** um veterinário informa senha atual errada ou novos campos inconsistentes
- **WHEN** solicita a troca
- **THEN** a operação é rejeitada sem modificar a senha ou encerrar a sessão por simples erro de validação

#### Scenario: Troca confirmada
- **GIVEN** credenciais atuais e nova confirmação válidas
- **WHEN** o backend confirma a troca
- **THEN** a sessão local é limpa, a nova senha permite login e a antiga deixa de permitir quando diferente

### Requirement: Edições pendentes e contexto ficam protegidos
O sistema SHALL preservar cancelamento, tentativas após falha, carregamento, proteção contra envio duplicado e confirmação de descarte em abas, menu, histórico e logout. Cache e resultados assíncronos SHALL ser isolados por token, perfil, identidade e geração de sessão; sessões encerradas/substituídas SHALL NOT restaurar dados antigos. Senhas SHALL ser limpas ao sair da aba e nunca armazenadas no navegador.

#### Scenario: Navegação com alteração não salva
- **WHEN** o médico tenta sair com nome ou telefone alterado
- **THEN** pode continuar editando ou descartar e executar o destino exato solicitado, incluindo Horários ou Consultas

#### Scenario: Resposta antiga de outro perfil
- **GIVEN** uma leitura iniciada em uma sessão de tutor ou veterinário
- **WHEN** essa sessão é encerrada ou substituída antes da resposta
- **THEN** a resposta antiga não altera os dados ou flags da sessão nova

#### Scenario: Tutor continua usando Configurações
- **WHEN** o tutor usa a mesma rota
- **THEN** mantém seu menu, CPF mascarado, endereço e endpoints exclusivos anteriores
