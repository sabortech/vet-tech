# Design

## Contexto

Consulte `proposal.md` para a motivação e `specs/tutor-registration/spec.md` para os contratos. A aplicação Reflex já alterna entre login e perfil autenticado, e o cliente HTTP já consome endpoints do grupo `Authentication`. O endpoint `tutor/login` autentica pela tabela `tutor`; `auth/signup` é um exemplo do Xano que cria registros na tabela `user` e não serve para este fluxo.

A tabela `tutor` já tem e-mail único e senha sensível, mas CPF ainda não tem índice único; nome, telefone e endereço são opcionais no schema atual. O domínio exige esses dados no cadastro. A tabela foi confirmada vazia no ambiente de desenvolvimento antes das restrições, sem registros incompletos ou CPFs duplicados a tratar. Os artefatos oficiais do Xano ficam exclusivamente em `xano/`; a árvore XanoScript existente na raiz é uma duplicata legada e deve ser removida após transferir para a árvore oficial as alterações desta mudança. Não há capacidade correspondente em `openspec/specs/`, então esta mudança introduz uma nova especificação.

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

Adicionar a operação `tutor/signup` no grupo `Authentication`, gravando na tabela `tutor`. Os arquivos canônicos ficam em `xano/api/authentication/auth/` e `xano/table/tutor.xs`. O endpoint valida os campos no servidor e usa o campo `password` do modelo para persistir credenciais no formato seguro esperado pelo Xano. A resposta confirma o resultado sem devolver senha, hash ou dados pessoais desnecessários. O endpoint não cria token: o tutor entra depois pelo `tutor/login`.

Alternativa considerada: reutilizar `auth/signup`. Rejeitada porque esse endpoint cria a identidade em `user`, enquanto o perfil e as operações protegidas usam `tutor`.

### Validar e normalizar CPF no backend e impor unicidade no armazenamento

Aceitar CPF com ou sem pontuação, normalizar para os 11 dígitos e validar os dígitos verificadores no backend. A interface pode repetir a validação para feedback antecipado, mas não é fonte de segurança. Criar índice único para CPF, além do índice de e-mail existente, e traduzir violações de unicidade em erro de campo compreensível.

Alternativa considerada: consultar duplicidade somente antes de inserir. Rejeitada porque duas requisições concorrentes poderiam passar pela consulta; a restrição no armazenamento fecha essa condição de corrida.

Na verificação do cadastro foi encontrado um defeito na chamada dos filtros de regex do XanoScript: as expressões de validação usavam o texto do CPF no lugar da expressão regular, e a normalização passava os argumentos de `regex_replace` em ordem inversa. Além disso, o validador do projeto não reconhece o alias `regex_test` usado no endpoint. O endpoint deve usar o padrão documentado com a expressão regular à esquerda (`regex_matches`/`regex_replace`) e o CPF como texto de entrada; assim, o backend remove pontuação antes de exigir 11 dígitos e executar a validação dos verificadores.

### Exigir os campos definidos pelo domínio no cadastro

O endpoint exige nome, CPF, e-mail, telefone, endereço e senha. Antes de tornar `nome`, `telefone` e `endereco` obrigatórios no schema, verificar registros existentes e planejar correção ou migração de dados incompletos. CPF também deve ser verificado quanto a duplicidades antes do índice único. E-mail é normalizado pelo modelo existente.

Alternativa considerada: manter campos sem obrigatoriedade no contrato e aceitar cadastro parcial. Rejeitada porque diverge das regras documentadas em `docs/domain-model.md`.

### Apresentar cadastro e login como modos da mesma entrada

Manter a rota raiz como ponto de acesso: um controle alterna entre os formulários de login e cadastro, sem definir layout visual. A composição da rota ficará em `vet_tech/pages/index.py`; a funcionalidade e o estado de autenticação/cadastro ficarão em `vet_tech/features/auth/`; componentes reutilizáveis do formulário ficarão em `vet_tech/components/`. `vet_tech/vet_tech.py` permanece como ponto de entrada Reflex e registra/importa as páginas.

O cadastro e o login devem compartilhar uma única fonte de estado de sessão; não duplicar token ou autenticação entre módulos. A extração deve preservar a integração existente com o perfil e o carregamento de pets após o login. Após sucesso no cadastro, limpar os dados de senha, mostrar confirmação e retornar ao login para autenticação manual. Em falha, mostrar o erro retornado e preservar os demais campos para permitir correção.

Alternativa considerada: autenticar automaticamente após criar a conta. Rejeitada conforme decisão do usuário; isso também exigiria que o endpoint emitisse token e alteraria o fluxo de sessão atual.

Alternativa considerada: manter toda a tela, o estado e o formulário em `vet_tech.py`. Rejeitada para o novo fluxo porque concentra responsabilidades e contraria a organização documentada em `docs/architecture.md`. A extração será limitada aos módulos necessários e não exige reorganizar todo o código de pets nesta mudança.

### Evitar registrar dados de credenciais e identidade em logs

Não incluir senha, hash ou payload completo de cadastro em mensagens, resposta ou logs da aplicação. Respostas devem conter somente confirmação ou erros de validação; não é necessário criar log de auditoria clínica para o cadastro.

Alternativa considerada: usar o log genérico do quick start, que recebe o registro como metadado. Rejeitada porque poderia propagar dados pessoais e usa a entidade `user`, não a identidade do tutor.

## Riscos / Trade-offs

- **[Risco]** Registros existentes podem não ter nome, telefone ou endereço, ou podem conter CPF duplicado → **Mitigação:** auditar a base antes de apertar restrições; corrigir dados ou realizar a migração necessária antes de publicar o endpoint.
- **[Risco]** Mensagens que distinguem CPF ou e-mail já cadastrado podem revelar existência de conta → **Mitigação:** expor somente o campo que precisa de correção, sem retornar dados da conta; avaliar proteção contra abuso no ambiente de implantação.
- **[Risco]** Validação de CPF apenas no navegador pode ser contornada → **Mitigação:** validar e normalizar no endpoint, com unicidade garantida também pelo índice.
- **[Risco]** Uma expressão de regex aceita pelo editor, mas chamada com argumentos na ordem errada ou alias não reconhecido, pode rejeitar CPFs válidos → **Mitigação:** usar a assinatura documentada dos filtros e validar todos os arquivos XanoScript no projeto; confirmar o comportamento funcional no ambiente Xano antes da publicação.
- **[Risco]** Reutilizar acidentalmente o endpoint de quick start criaria usuário fora do domínio → **Mitigação:** testar que o novo fluxo cria somente em `tutor` e não em `user`.

## Plano de migração

1. Verificar registros existentes em `xano/table/tutor.xs` para campos requeridos, CPFs inválidos/duplicados e compatibilidade do índice atual de e-mail.
2. Corrigir ou tratar os registros que impediriam tornar os campos obrigatórios e criar o índice único de CPF em `xano/table/tutor.xs`.
3. Implementar e validar `tutor/signup` em `xano/api/authentication/auth/` em ambiente de desenvolvimento antes de expô-lo ao Reflex.
4. Consolidar as alterações desta mudança na árvore canônica `xano/` e remover as cópias XanoScript da raiz, sem remover recursos não Xano.
5. Criar os módulos da página raiz, da funcionalidade de autenticação e dos componentes necessários, mantendo `vet_tech.py` como ponto de entrada; verificar imports e registro da rota raiz.
6. Integrar o formulário ao cliente Xano existente e verificar cadastro, duplicidades, erros, retorno à tela de login e preservação do login e do perfil de pets.

Se a verificação de dados apontar conflitos não resolvidos, não publicar a restrição nem o cadastro até decidir como corrigi-los. Para rollback, desabilitar o endpoint e o modo de cadastro; preservar contas existentes e não remover índices sem confirmar o impacto nas contas já criadas.
