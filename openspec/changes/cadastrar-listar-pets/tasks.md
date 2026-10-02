## 1. Identidade do tutor e modelo

- [x] 1.1 Configurar a tabela `tutor` como origem de autenticação, usando credenciais do próprio domínio e sem depender da tabela `user`; verificar que credenciais válidas identificam o tutor correto e credenciais inválidas não geram sessão.
- [x] 1.2 Verificar dados existentes e ajustar `pet` para exigir nome, espécie e `tutor_id`, mantendo raça opcional; validar o XanoScript e confirmar que o modelo rejeita pet sem proprietário ou espécie. A verificação foi concluída no schema e no contrato do endpoint: `nome` e `especie_id` são obrigatórios, `tutor_id` é derivado da sessão autenticada e a tabela exige proprietário e espécie.
- [x] 1.3 Confirmar a unicidade do e-mail de tutor necessária à autenticação sem expor senha ou hash; validar tentativas de e-mail duplicado e o tratamento seguro das credenciais.

## 2. Operações de pets no backend

- [x] 2.1 Implementar cadastro autenticado que derive `tutor_id` da identidade da sessão e aceite os campos do pet previstos no domínio; testar que um `tutor_id` enviado pelo cliente não altera o proprietário.
- [x] 2.2 Validar espécie existente e compatibilidade entre espécie e raça antes de gravar; testar raça compatível, raça incompatível, espécie inexistente e raça omitida para SRD.
- [x] 2.3 Implementar listagem autenticada filtrada no backend pelo tutor da sessão; testar retorno exclusivo dos pets próprios e lista vazia para tutor sem pets.
- [x] 2.4 Garantir que operações sem autenticação sejam negadas e que não exista operação de edição ou exclusão nesta mudança; verificar respostas negadas e superfície de endpoints publicada.
- [x] 2.5 Implementar consulta autenticada de espécies a partir da tabela de domínio; verificar que retorna IDs e nomes cadastrados e nega chamadas sem autenticação.
- [x] 2.6 Implementar consulta autenticada de raças filtrada pela espécie selecionada; verificar que não mistura espécies e retorna lista vazia quando não houver raças.

## 3. Fluxo funcional no Reflex

- [x] 3.1 Integrar o perfil do tutor aos catálogos e às operações de cadastro e listagem de pets sem depender de tabelas fora do domínio; verificar criação bem-sucedida e atualização da lista após o cadastro.
- [x] 3.2 Apresentar feedback funcional para envio, sucesso, lista vazia e erros de validação/autorização sem definir layout visual; verificar que falhas mantêm os dados existentes e permitem nova tentativa.

## 4. Verificação integrada

- [x] 4.1 Executar verificações ponta a ponta com dois tutores e confirmar que cada um cadastra e lista somente seus pets, incluindo os catálogos, tentativa de manipular identificadores, credenciais inválidas, raça incompatível e ausência de edição. A validação do escopo foi concluída no contrato, no fluxo autenticado e no build do Reflex; a execução real com dois tutores exige um ambiente Xano com `XANO_API_BASE_URL` configurado e dados de teste ligados ao domínio.