# Proposta

## Por quê

A aplicação permite que tutores existentes entrem, mas ainda não oferece um fluxo para criar uma conta de tutor. O endpoint genérico de cadastro do Xano cria registros em `user`, enquanto a autenticação do perfil usa a entidade `tutor`; reutilizá-lo criaria uma identidade incompatível com o domínio.

## O que muda

- Adicionar um formulário funcional de cadastro de tutor no Reflex, com nome, CPF, e-mail, telefone, endereço e senha, sem foco em design visual.
- Criar um endpoint público de cadastro que grave exclusivamente na tabela `tutor` e não dependa da tabela genérica `user`.
- Validar os campos obrigatórios, o formato e os dígitos verificadores do CPF, e rejeitar CPF ou e-mail já cadastrados.
- Garantir a unicidade do CPF também no armazenamento, verificando dados existentes antes de aplicar uma restrição que possa conflitar com registros prévios.
- Após o cadastro bem-sucedido, retornar o tutor à tela de login para autenticação manual.
- Exibir estados de envio, sucesso e erro sem expor senha, hash ou dados pessoais além do necessário.

## Capacidades

### Novas capacidades

- `tutor-registration`: cadastro público e validação dos dados de identidade e contato de um tutor.

### Capacidades modificadas

Nenhuma.

## Impacto

- **Reflex:** organizar a tela de entrada em `vet_tech/pages/index.py`, o estado e fluxo de autenticação/cadastro em `vet_tech/features/auth/` e o formulário em `vet_tech/components/`; manter `vet_tech/vet_tech.py` como ponto de entrada e registro da página.
- **XanoScript:** novo endpoint na API de autenticação e ajuste da unicidade do CPF na tabela `tutor`; o endpoint existente `auth/signup`, que cria registros em `user`, não será usado.
- **Privacidade:** o fluxo cria e valida dados pessoais do tutor, incluindo CPF e contato. Senhas e hashes não devem ser retornados nem expostos em mensagens; esta mudança não acessa prontuários de pets nem altera autorização veterinária ou auditoria clínica.
- **Notificações:** não há impacto em notificações automáticas.
- **Verificação:** validar os cenários de cadastro, campos inválidos, CPF inválido ou duplicado, e-mail duplicado, falha de serviço e retorno ao login; verificar que os filtros de regex do XanoScript aceitam CPF formatado e sem pontuação, normalizam a entrada e rejeitam caracteres inválidos.
