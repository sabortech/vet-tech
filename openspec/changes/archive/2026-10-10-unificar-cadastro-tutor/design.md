# Design

## Context

`pages/cadastro.py` contém o design, mas seu botão chama um evento vazio. `components/auth.py` contém o formulário funcional. A API exige endereço, ausente no design. A branch já recebeu as mudanças da main; preservar as alterações preparadas pelo usuário.

## Goals / Non-Goals

**Goals:** manter uma única rota e composição de cadastro, reutilizando o evento de API e a normalização do CPF.

**Non-Goals:** OAuth Google, persistência de dados pessoais, publicação de termos legais, alterações Xano e redesign do login.

## Decisions

- Manter `/cadastro` e seu design, convertendo os campos em um `rx.form` com nomes do contrato da API. Evita copiar a lógica em dois formulários.
- Encaminhar o botão do login para `/cadastro`, remover o formulário antigo e suas variáveis de apresentação. O perfil e a autenticação existentes continuam independentes.
- Validar confirmação de senha antes da chamada Xano; usar CPF controlado e campos restantes enviados pelo formulário. Dados permanecem após erro; sucesso redireciona ao login e limpa o formulário pela desmontagem.
- Exibir Google desabilitado com aviso; retirar lembrar informações, sem prometer persistência inexistente. A caixa de aceite visual não representa registro legal auditável; não criar essa obrigação nesta integração.
- Substituir alturas fixas por altura automática e permitir rolagem em telas pequenas para acomodar endereço e mensagens.

## Risks / Trade-offs

- Campos extras aumentam a altura → conteúdo responsivo sem corte e painel ilustrado apenas em telas maiores.
- Mudança de rota após sucesso → testar mensagem de confirmação e ausência de autenticação automática.
- API externa → testes com respostas simuladas verificam o contrato; integração real anterior está documentada no cadastro arquivado.
