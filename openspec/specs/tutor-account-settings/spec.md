# Configurações da conta do tutor

## Purpose

Permitir que o tutor consulte e mantenha os dados permitidos da própria conta e altere sua senha com validação no servidor, em uma interface consistente com o Vet Tech.

## Requirements

### Requirement: Configurações apresentam a identidade visual e as seções aprovadas
O sistema SHALL apresentar em `/configuracoes` o título Configurações e as abas Minha conta, Segurança e Preferências, inicialmente em Minha conta, com somente o conteúdo da aba selecionada. SHALL reutilizar a sidebar, Nunito, cores, cartões, campos e botões existentes, seguindo os protótipos fornecidos. A tartaruguinha SHALL aparecer na linha das abas, ao lado de Preferências em desktop, sem obstruir controles. O cartão de Segurança SHALL ser compacto e centralizado na área de conteúdo, com largura máxima de 640 px, cabeçalho e ação centralizados. O layout SHALL adaptar-se a desktop e celular sem rolagem horizontal.

#### Scenario: Tutor abre as configurações
- **WHEN** o tutor autenticado acessa a tela
- **THEN** Minha conta está selecionada e apresenta Dados pessoais com identificação Perfil: Tutor
- **AND** a sidebar identifica Configurações como área ativa

#### Scenario: Tutor alterna seções
- **WHEN** o tutor seleciona Segurança ou Preferências sem alterações pendentes
- **THEN** vê somente o formulário de senha ou os cartões Aparência e Navegação, respectivamente
- **AND** não vê quadros flutuantes sobre outras abas

#### Scenario: Acesso em celular ou por teclado
- **WHEN** a tela é usada em 390 px ou por teclado
- **THEN** os campos ficam em uma coluna quando necessário, abas e ações são acessíveis, o foco é visível e a mascote não encobre conteúdo

### Requirement: Consulta da conta é limitada ao tutor autenticado
O backend SHALL identificar a conta pela autenticação de tutor, sem usar identificador escolhido pelo cliente. SHALL retornar somente nome, e-mail, CPF mascarado, telefone e endereço necessários à tela, sem senha, hash ou CPF completo. Sessões ausentes, inválidas ou de outro domínio SHALL ser rejeitadas sem exposição de dados pessoais.

#### Scenario: Tutor consulta os próprios dados
- **GIVEN** uma sessão válida de tutor
- **WHEN** seus dados são consultados
- **THEN** somente os dados dessa conta são retornados e o CPF aparece parcialmente mascarado

#### Scenario: Cliente tenta escolher outra identidade
- **GIVEN** um cliente tenta fornecer o identificador de outro tutor
- **WHEN** solicita dados de conta
- **THEN** esse identificador não concede acesso à outra conta

#### Scenario: Sessão sem identidade de tutor
- **GIVEN** uma requisição sem autenticação válida de tutor, inclusive token de user ou veterinário
- **WHEN** solicita dados de conta
- **THEN** o backend nega a consulta sem retornar dados pessoais

### Requirement: Edição permite somente nome telefone e endereço
O sistema SHALL permitir atualizar nome completo, telefone e endereço obrigatórios, mantendo e-mail somente leitura e CPF mascarado somente leitura. O backend SHALL persistir somente os três campos permitidos da conta autenticada, sem alterar identidade, e-mail, CPF, senha ou vínculos mesmo se enviados fora do formulário. Valores vazios após remoção de espaços externos SHALL ser rejeitados antes de qualquer gravação.

#### Scenario: Edição válida
- **GIVEN** um tutor autenticado altera nome, telefone ou endereço com valores válidos
- **WHEN** confirma Salvar alterações e o backend conclui a escrita
- **THEN** recebe confirmação e uma nova consulta mostra os dados persistidos

#### Scenario: Tentativa de alterar campos protegidos ou outro tutor
- **GIVEN** um tutor envia e-mail, CPF, senha, vínculos ou identidade de outra conta junto da atualização
- **WHEN** o backend processa a requisição
- **THEN** nenhum campo protegido nem dado de outra conta é modificado

#### Scenario: Validação e falha preservam o formulário
- **WHEN** um campo obrigatório está vazio ou o salvamento falha
- **THEN** o sistema identifica a falha, mantém os dados editados e não confirma sucesso
- **AND** valores inválidos não são gravados parcialmente

### Requirement: Formulários refletem carregamento e alterações pendentes
O sistema SHALL apresentar carregamento antes de consultar ou salvar, impedir envios duplicados durante uma operação e distinguir formulário limpo de formulário alterado. Cancelar SHALL restaurar a última versão carregada ou salva. Falha no carregamento SHALL apresentar tentativa novamente, sem liberar salvamento de campos vazios como se fossem dados reais.

#### Scenario: Operação em andamento
- **WHEN** consulta ou atualização está em andamento
- **THEN** a tela indica a operação e impede envio duplicado ou edição antes da carga inicial

#### Scenario: Cancelar edição
- **WHEN** o tutor cancela uma edição ainda não salva
- **THEN** os campos voltam à última versão confirmada e o formulário deixa de indicar alterações pendentes

#### Scenario: Falha ao carregar
- **WHEN** os dados não podem ser carregados
- **THEN** a tela mostra erro e permite tentar novamente sem inventar valores ou confirmar salvamento

### Requirement: Troca de senha valida a credencial atual no backend
O sistema SHALL exigir senha atual, nova senha e confirmação; a nova senha SHALL ser não vazia e coincidir exatamente com a confirmação. SHALL preservar os caracteres das senhas, sem remover espaços silenciosamente, e permitir mostrar ou ocultar cada campo. O backend SHALL validar a senha atual contra a conta de tutor autenticada e armazenar a nova senha como hash, sem retornar ou registrar credenciais. Não SHALL introduzir regra de complexidade ou tamanho mínimo diferente da política atual do tutor nesta change.

#### Scenario: Senha atual inválida
- **GIVEN** um tutor autenticado informa senha atual incorreta
- **WHEN** solicita a troca
- **THEN** o backend rejeita a operação e a senha existente permanece válida

#### Scenario: Nova senha ausente ou confirmação divergente
- **WHEN** a nova senha está vazia ou diverge da confirmação
- **THEN** o sistema apresenta erro antes da chamada e o backend também rejeita uma requisição direta inconsistente sem escrita

#### Scenario: Troca confirmada encerra a sessão atual
- **GIVEN** a senha atual é válida e os novos campos são consistentes
- **WHEN** o backend confirma a atualização
- **THEN** a interface limpa campos de senha, dados de conta e sessão atual e redireciona para `/login` com confirmação
- **AND** um novo login aceita a nova senha e rejeita a anterior quando elas são diferentes

#### Scenario: Campos de senha deixam de ser usados
- **WHEN** o tutor sai da seção Segurança ou encerra a sessão
- **THEN** os campos de senha e seus estados de visibilidade são limpos, sem persistência em armazenamento do navegador

### Requirement: Respostas atrasadas não restauram dados de sessão encerrada
O sistema SHALL descartar resultados de carregamento ou salvamento iniciados em uma sessão que foi encerrada ou substituída. Falhas temporárias SHALL ter mensagens seguras, sem reproduzir corpos arbitrários ou repetir automaticamente uma operação de escrita. Rejeição de autenticação SHALL limpar a sessão e conduzir ao login, distinguindo-se de erro de validação da senha atual.

#### Scenario: Resposta chega depois de sair
- **GIVEN** uma consulta da conta está em andamento
- **WHEN** a sessão é encerrada ou substituída antes da resposta
- **THEN** os dados da sessão antiga não aparecem na interface nem sobrescrevem a nova conta

#### Scenario: API temporariamente indisponível
- **WHEN** o serviço retorna timeout, erro de rede ou limite de solicitações
- **THEN** a tela informa a falha com mensagem segura, libera os controles apropriados e não repete automaticamente a escrita
