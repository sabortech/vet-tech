# Verificação de cadastro de tutor

## Resultados de 2026-10-10

- O usuário confirmou o cadastro após publicar a correção dos filtros de CPF.
- A cópia atual do endpoint publicado `tutor/signup` contém os filtros de regex
  corrigidos. A tabela publicada possui índices únicos de CPF e e-mail.
- `python -m unittest discover -s tests/unit -v`: 8 testes aprovados.
- `python -m reflex compile --dry`: compilação aprovada.
- Validador oficial de XanoScript (`@xano/developer-mcp` em cache): os 39 arquivos
  existentes em `xano/` e a nova definição de workflow foram aprovados.
- Suíte `tests/integration/test_signup_api_rejections.py`, executada contra o
  endpoint publicado: 5 testes aprovados, incluindo os seis campos obrigatórios
  ausentes individualmente, CPF curto, dígitos repetidos, dígitos verificadores
  incorretos e letras no CPF. Todas as tentativas foram rejeitadas com HTTP 400.

## Testes preparados inicialmente

- `xano/workflow_test/cadastro_tutor.xs`: teste nativo inicial para CPF inválido,
  com contagens de `tutor` e `user` antes/depois, usando cópia de datasource.
- `tests/integration/run_xano_signup_workflow.py`: instala e executa esse teste
  pelo contrato oficial da Metadata API, usando o perfil autenticado do CLI e
  sem imprimir credenciais, payloads ou registros pessoais.
- A suíte de rejeições só executa remotamente quando `XANO_TEST_AUTH_URL` é
  informado; não cria contas e permanece separada dos testes unitários.

## Impedimento e pendências

O Xano recusou o sandbox com `Access Denied. Not supported with Free plan.` e
recusou a instalação do workflow com HTTP 403 e
`Please upgrade to access this feature.` O workflow não foi instalado nem
executado; sua validação local não comprova as contagens no banco remoto.

Nesse momento, as tarefas 1.4 e 3.1 permaneciam abertas. Ainda faltavam os cenários de
cadastro com fixtures, CPF/e-mail duplicados, falha de persistência e ausência
de contas parciais ou registros em `user`, além do login real após o cadastro.
O sucesso informado pelo usuário não substitui essa cobertura automatizada.

O usuário posteriormente confirmou que o workspace é de desenvolvimento e
autorizou a criação e remoção de contas fictícias temporárias.

## Conclusão por testes externos no workspace de desenvolvimento

A suíte `tests/integration/run_tutor_registration_live.py` foi executada contra
os endpoints publicados e concluiu 21 verificações, incluindo preparação,
cenários funcionais, concorrência e limpeza. Ela usa o perfil autenticado do
Xano CLI e cria emails exclusivos por execução, com domínio `example.invalid`.
Não imprime CPFs, senhas, tokens nem registros pessoais.

Cobertura confirmada:

- Cadastro válido com CPF somente numérico e resposta contendo apenas sucesso,
  sem senha, hash ou token de autenticação automática.
- CPF formatado normalizado para 11 dígitos, preservando zero inicial.
- Ausência individual de nome, CPF, email, telefone, endereço e senha.
- CPF curto, repetido, com verificador incorreto e com letras.
- CPF duplicado e email duplicado com diferença de maiúsculas/minúsculas.
- Login real após cadastro, incluindo normalização do email, e rejeição de
  senha incorreta.
- Conferência dos registros após cada rejeição: nenhuma conta parcial nas
  fixtures e nenhum registro correspondente em `user`.
- Cadastro concorrente: exatamente uma conta por grupo de quatro requisições;
  as demais são rejeitadas pela validação ou pelo índice único.
- Falha de persistência confirmada separadamente: três requisições concorrentes
  retornaram HTTP 500, `ERROR_FATAL` e mensagem com indicação de duplicidade,
  enquanto uma retornou sucesso; somente uma conta foi gravada e nenhum registro
  foi criado em `user`. O teste distingue esse erro da rejeição antecipada com
  HTTP 400. Uma tentativa diagnóstica anterior usava uma busca textual estreita
  demais para reconhecer a mensagem do Xano; a detecção foi ajustada e confirmada
  antes de considerar a tarefa concluída.
- Limpeza de todas as fixtures de cada execução, com conferência de que todos os
  IDs preexistentes em `tutor` e `user` continuam presentes. O teste recusa remover
  registros anteriores à execução ou emails fora do seu próprio identificador.

Os testes nativos pagos não foram instalados. A cobertura necessária foi
executada pela API real e pelo banco remoto, sem alterar endpoints, schema,
índices, planos ou permissões do workspace. As definições preliminares do teste
nativo foram substituídas pela suíte externa compatível com o ambiente.

As evidências acima, os oito testes unitários aprovados, a compilação Reflex e a
validação dos 39 arquivos XanoScript satisfazem as tarefas 1.4 e 3.1. A validação
do formulário é coberta pelos testes do estado Reflex e pela compilação; esta
execução não incluiu automação visual do navegador.

Para repetir em um workspace de desenvolvimento autorizado:

```powershell
python tests/integration/run_tutor_registration_live.py --profile vettech --allow-temporary-accounts
```

São necessários `httpx` e `PyYAML`. O teste de concorrência precisa observar ao
menos uma rejeição efetiva na persistência; se todas forem rejeitadas antes da
inserção, ele falha explicitamente em vez de declarar cobertura desse cenário.
