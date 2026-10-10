# Tasks

## 1. Modelo e cadastro no Xano

- [x] 1.1 Verificar no ambiente de desenvolvimento se tutores existentes têm nome, CPF, telefone e endereço válidos e se há CPF duplicado; registrar apenas o resultado agregado e resolver conflitos antes de aplicar restrições.
- [x] 1.2 Ajustar `xano/table/tutor.xs` para exigir os campos obrigatórios do domínio e adicionar unicidade ao CPF; confirmar que e-mail e CPF duplicados não podem ser persistidos.
- [x] 1.3 Criar `tutor/signup` em `xano/api/authentication/auth/`, validando e normalizando campos no backend, criando somente em `tutor` e usando o tipo de senha seguro; confirmar que a resposta não contém senha ou hash. Corrigir as expressões de regex para seguir a assinatura do XanoScript e passar na validação local.
- [x] 1.4 Adicionar testes do endpoint no ambiente Xano para cadastro válido, campos ausentes, CPF inválido/duplicado, e-mail duplicado e falha de persistência; confirmar que os casos inválidos não deixam conta parcial nem criam registros em `user`. Verificado por testes HTTP externos com fixtures temporárias e auditoria via Metadata API; resultados em `verification.md`.

## 2. Formulário no Reflex

- [x] 2.1 Extrair a composição da rota raiz para `vet_tech/pages/index.py` e mantê-la registrada pelo ponto de entrada `vet_tech/vet_tech.py`; verificar que a rota raiz continua carregando no build Reflex.
- [x] 2.2 Implementar o estado e os fluxos de login/cadastro em `vet_tech/features/auth/`, preservando uma única fonte de estado de sessão e a integração com o perfil e o carregamento dos pets; testar login e navegação para o perfil sem regressões.
- [x] 2.3 Criar em `vet_tech/components/` o formulário reutilizável de cadastro e conectá-lo à view de autenticação; verificar campos obrigatórios e feedback antecipado de CPF sem substituir validações do Xano.
- [x] 2.4 Integrar o envio ao endpoint `tutor/signup`; testar estados de envio, erros recuperáveis, sucesso, limpeza da senha e retorno ao login sem autenticação automática.

## 3. Verificação integrada

- [x] 3.1 Executar os testes relevantes, validar todos os arquivos XanoScript alterados em `xano/` e compilar a aplicação Reflex; confirmar no ambiente Xano o fluxo completo de cadastro, tentativa de login após cadastro e mensagens para CPF/e-mail duplicados. Concluído com oito testes unitários, compilação Reflex, validação de 39 arquivos XanoScript e testes HTTP/banco no workspace de desenvolvimento; resultados em `verification.md`.
- [x] 3.2 Consolidar os artefatos XanoScript em `xano/`, transferir para lá as alterações de cadastro/schema e remover as cópias XanoScript da raiz sem remover recursos não Xano.
