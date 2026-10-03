# Tasks

## 1. Modelo e cadastro no Xano

- [ ] 1.1 Verificar no ambiente de desenvolvimento se tutores existentes têm nome, CPF, telefone e endereço válidos e se há CPF duplicado; registrar apenas o resultado agregado e resolver conflitos antes de aplicar restrições.
- [ ] 1.2 Ajustar `tutor` para exigir os campos obrigatórios do domínio e adicionar unicidade ao CPF; validar o XanoScript e confirmar que e-mail e CPF duplicados não podem ser persistidos.
- [ ] 1.3 Criar `tutor/signup` no grupo `Authentication`, validando e normalizando campos no backend, criando somente em `tutor` e usando o tipo de senha seguro; validar o XanoScript e confirmar que a resposta não contém senha ou hash.
- [ ] 1.4 Adicionar testes do endpoint para cadastro válido, campos ausentes, CPF inválido/duplicado, e-mail duplicado e falha de persistência; confirmar que os casos inválidos não deixam conta parcial nem criam registros em `user`.

## 2. Formulário no Reflex

- [ ] 2.1 Adicionar o modo de cadastro acessível a partir do login, com nome, CPF, e-mail, telefone, endereço e senha; verificar que os campos obrigatórios e a validação antecipada do CPF dão feedback sem substituir a validação do servidor.
- [ ] 2.2 Integrar o envio ao endpoint `tutor/signup`; testar estados de envio, erros recuperáveis, sucesso, limpeza da senha e retorno ao login sem autenticação automática.

## 3. Verificação integrada

- [ ] 3.1 Executar os testes relevantes, validar todos os arquivos XanoScript alterados e compilar a aplicação Reflex; confirmar o fluxo completo de cadastro, tentativa de login após cadastro e mensagens para CPF/e-mail duplicados.
