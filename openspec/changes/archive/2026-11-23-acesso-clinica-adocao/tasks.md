# Tasks

## 1. Identidade e isolamento de clínica

- [x] 1.1 Criar identidade administrativa individual, provisionamento restrito e autenticação Xano; testar credenciais inválidas, conta inativa e ausência de cadastro público.
- [x] 1.2 Implementar listagem de veterinários vinculados à clínica da sessão; testar isolamento entre clínicas e profissionais sem vínculo.
- [x] 1.3 Criar conta de teste solicitada somente em ambiente isolado, sem registrar credenciais nos arquivos; verificar login e manter a conta disponível para os testes solicitados pelo usuário.

## 2. Responsabilidade e gestão de pets

- [x] 2.1 Migrar modelo para exatamente um responsável, clínica ou tutor; verificar pets legados, exclusividade e atualizar DER e documentação de domínio.
- [x] 2.2 Revisar endpoints que dependem de `tutor_id` e testar que pets de clínica não são acessíveis como pets de tutor nem concedem acesso clínico indevido.
- [x] 2.3 Implementar cadastro de pet novo e publicação/retirada pela clínica autenticada; testar validação, disponibilidade inicial e negação entre clínicas e após adoção.
- [x] 2.4 Registrar eventos administrativos transacionais e protegidos; testar autoria, ausência de credenciais e rollback diante de falha de auditoria.

## 3. Adoção e interface

- [x] 3.1 Adaptar listagem e transferência atômica de clínica para tutor com trava compartilhada; testar preservação de histórico, revogação e projeção clínica restrita.
- [x] 3.2 Criar acesso e área Reflex da clínica com profissionais e cadastro/gestão de pets; verificar navegação, formulários, estados vazios, falhas, acessibilidade e responsividade.
- [x] 3.3 Integrar pets da clínica à área de adoção existente do tutor; testar visualização, confirmação, atualização de listas e regressões de pets de tutor.

## 4. Verificação integrada

- [x] 4.1 Em Xano de desenvolvimento isolado com dados sintéticos, validar autenticação, isolamento entre clínicas, concorrência entre publicação/retirada/adoção e transferência única; registrar evidências.
- [x] 4.2 Executar testes unitários e de navegador relevantes, validação OpenSpec e compilação Reflex; documentar resultados e limitações de publicação.
- [x] 4.3 Documentar provisionamento, operação, migração e rollback; verificar que nenhuma credencial ou dado real foi incluído no repositório.
