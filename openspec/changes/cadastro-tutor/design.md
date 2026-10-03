# Design

## Contexto

Consulte `proposal.md` para a motivação e `specs/tutor-registration/spec.md` para os contratos. A aplicação Reflex já alterna entre login e perfil autenticado, e o cliente HTTP já consome endpoints do grupo `Authentication`. O endpoint `tutor/login` autentica pela tabela `tutor`; `auth/signup` é um exemplo do Xano que cria registros na tabela `user` e não serve para este fluxo.

A tabela `tutor` já tem e-mail único e senha sensível, mas CPF ainda não tem índice único; nome, telefone e endereço são opcionais no schema atual. O domínio exige esses dados no cadastro. Não há capacidade correspondente em `openspec/specs/`, então esta mudança introduz uma nova especificação.

## Objetivos / Não objetivos

**Objetivos:**

- Integrar o cadastro ao fluxo existente de autenticação de tutores sem criar uma segunda identidade.
- Revalidar no backend todos os dados que determinam a criação da conta.
- Preservar a escolha de voltar ao login após o cadastro, sem iniciar uma sessão automaticamente.

**Não objetivos:**

- Implementar cadastro de veterinário, recuperação de senha, confirmação por e-mail ou autenticação multifator.
- Definir identidade visual ou criar um fluxo de onboarding além do retorno ao login.
- Criar perfil/pet, acessar prontuário, alterar autorização veterinária ou adicionar notificações.

## Decisões

### Criar o tutor pela API própria, não pelo cadastro genérico

Adicionar a operação `tutor/signup` no grupo `Authentication`, gravando na tabela `tutor`. O endpoint valida os campos no servidor e usa o campo `password` do modelo para persistir credenciais no formato seguro esperado pelo Xano. A resposta confirma o resultado sem devolver senha, hash ou dados pessoais desnecessários. O endpoint não cria token: o tutor entra depois pelo `tutor/login`.

Alternativa considerada: reutilizar `auth/signup`. Rejeitada porque esse endpoint cria a identidade em `user`, enquanto o perfil e as operações protegidas usam `tutor`.

### Validar e normalizar CPF no backend e impor unicidade no armazenamento

Aceitar CPF com ou sem pontuação, normalizar para os 11 dígitos e validar os dígitos verificadores no backend. A interface pode repetir a validação para feedback antecipado, mas não é fonte de segurança. Criar índice único para CPF, além do índice de e-mail existente, e traduzir violações de unicidade em erro de campo compreensível.

Alternativa considerada: consultar duplicidade somente antes de inserir. Rejeitada porque duas requisições concorrentes poderiam passar pela consulta; a restrição no armazenamento fecha essa condição de corrida.

### Exigir os campos definidos pelo domínio no cadastro

O endpoint exige nome, CPF, e-mail, telefone, endereço e senha. Antes de tornar `nome`, `telefone` e `endereco` obrigatórios no schema, verificar registros existentes e planejar correção ou migração de dados incompletos. CPF também deve ser verificado quanto a duplicidades antes do índice único. E-mail é normalizado pelo modelo existente.

Alternativa considerada: manter campos sem obrigatoriedade no contrato e aceitar cadastro parcial. Rejeitada porque diverge das regras documentadas em `docs/domain-model.md`.

### Apresentar cadastro e login como modos da mesma entrada

Manter a entrada atual do app como ponto de acesso: um controle alterna entre o formulário de login e o de cadastro, sem definir layout visual. Após sucesso, limpar os dados de senha, mostrar confirmação e retornar ao login para autenticação manual. Em falha, mostrar o erro retornado e preservar os demais campos para permitir correção.

Alternativa considerada: autenticar automaticamente após criar a conta. Rejeitada conforme decisão do usuário; isso também exigiria que o endpoint emitisse token e alteraria o fluxo de sessão atual.

### Evitar registrar dados de credenciais e identidade em logs

Não incluir senha, hash ou payload completo de cadastro em mensagens, resposta ou logs da aplicação. Respostas devem conter somente confirmação ou erros de validação; não é necessário criar log de auditoria clínica para o cadastro.

Alternativa considerada: usar o log genérico do quick start, que recebe o registro como metadado. Rejeitada porque poderia propagar dados pessoais e usa a entidade `user`, não a identidade do tutor.

## Riscos / Trade-offs

- **[Risco]** Registros existentes podem não ter nome, telefone ou endereço, ou podem conter CPF duplicado → **Mitigação:** auditar a base antes de apertar restrições; corrigir dados ou realizar a migração necessária antes de publicar o endpoint.
- **[Risco]** Mensagens que distinguem CPF ou e-mail já cadastrado podem revelar existência de conta → **Mitigação:** expor somente o campo que precisa de correção, sem retornar dados da conta; avaliar proteção contra abuso no ambiente de implantação.
- **[Risco]** Validação de CPF apenas no navegador pode ser contornada → **Mitigação:** validar e normalizar no endpoint, com unicidade garantida também pelo índice.
- **[Risco]** Reutilizar acidentalmente o endpoint de quick start criaria usuário fora do domínio → **Mitigação:** testar que o novo fluxo cria somente em `tutor` e não em `user`.

## Plano de migração

1. Verificar registros existentes em `tutor` para campos requeridos, CPFs inválidos/duplicados e compatibilidade do índice atual de e-mail.
2. Corrigir ou tratar os registros que impediriam tornar os campos obrigatórios e criar o índice único de CPF.
3. Implementar e validar o endpoint `tutor/signup` em ambiente de desenvolvimento antes de expô-lo ao Reflex.
4. Integrar o formulário e verificar cadastro, duplicidades, erros e retorno à tela de login.

Se a verificação de dados apontar conflitos não resolvidos, não publicar a restrição nem o cadastro até decidir como corrigi-los. Para rollback, desabilitar o endpoint e o modo de cadastro; preservar contas existentes e não remover índices sem confirmar o impacto nas contas já criadas.
