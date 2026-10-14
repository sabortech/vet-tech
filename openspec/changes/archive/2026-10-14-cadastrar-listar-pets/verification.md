# Verificação da correção de listagem — 14/10/2026

## Problema reproduzido

Com uma resposta válida de `GET /pets` e falha no catálogo de raças, o
frontend deixava de atribuir a lista recebida a `State.pets`. A consulta era
feita inclusive para pets SRD. Falha no catálogo de espécies após autenticação
válida também desfazia a sessão antes de consultar os pets.

Não foi identificado qual campo está vazio no registro real relatado pelo
usuário. Raça e demais campos opcionais vazios são válidos; tutor e espécie
continuam obrigatórios no backend.

## Correção e evidências locais

- Raça ausente é exibida como SRD sem consulta de raças.
- Falha no catálogo de raças mantém os pets retornados visíveis e informa o erro.
- Falha no catálogo de espécies preserva o login válido e permite carregar pets.
- Nova sessão limpa pets e catálogos anteriores antes do carregamento.
- Cadastro sem raça envia somente nome e espécie, usando o token da sessão,
  e atualiza a lista após sucesso; não envia proprietário escolhido pelo cliente.
- Lista vazia limpa os pets anteriores; falha de listagem preserva dados da
  sessão atual e informa o erro.
- `./.venv/Scripts/python.exe -m unittest discover -s tests/unit -v`: 17 testes aprovados.
- `./.venv/Scripts/reflex.exe compile --dry`: compilação aprovada com Reflex 0.9.11.

## Autorização e limite da verificação

O XanoScript de listagem exige `auth = "tutor"` e aplica
`$this.tutor_id == $auth.id`. O cadastro deriva `tutor_id` de `$auth.id`.
Os endpoints publicados de pets, espécies e raças retornaram HTTP 401 sem
autenticação. Nenhum registro remoto foi criado ou alterado.

Não foi executado o teste autenticado com dois tutores na API publicada.
A tarefa 4.1 foi reaberta para refletir essa pendência. Pets com tutor ausente
ou incorreto no banco não serão corrigidos pelo frontend e precisam ser
investigados no Xano caso a lista continue vazia após esta correção.

## Investigação no Xano da conta de teste

A leitura da API de metadados confirmou o tutor ID 1 da conta de teste
indicada pelo usuário e dois pets: Rodolfo (ID 1) e Robson (ID 2), ambos com
`tutor_id = 1`, `especie_id = 1` e `raca_id = 0`. Nenhum vínculo foi alterado.

O endpoint publicado ainda usava `$this.tutor_id` no filtro. A documentação
oficial de Database Operations define referências a colunas como
`$db.<tabela>.<campo>`. Corrigidas as referências no filtro de pets e raças,
mantendo a autenticação e a filtragem no backend. A observação anterior de
que o filtro estava correto foi incompleta: a comparação representava a
regra correta, mas usava a referência incorreta para a coluna.

O push da foto opcional concluiu com sucesso (1 documento). O endpoint
publicado foi relido e confirmou `file? foto?`.

O dry-run dos filtros mostrou somente dois endpoints atualizados. O push
concluiu com sucesso (2 documentos); a releitura da API de metadados confirmou
os filtros corrigidos e `xanoscript.status = "ok"` em ambos. A chamada pública
sem token continuou retornando HTTP 401. Ainda falta a confirmação do retorno
autenticado na tela e do isolamento entre duas contas; não foi solicitada nem
alterada a senha da conta de teste.

Referência: https://docs.xano.com/xanoscript/function-reference/database-operations.md

## Encerramento por validação manual da equipe

Após a publicação das correções, o usuário confirmou que realizou os testes
da tarefa 4.1 manualmente com sua equipe e autorizou o arquivamento da change.
A tarefa foi concluída com base nessa confirmação, substituindo a pendência
registrada nas etapas anteriores. O agente não executou esses testes nem
recebeu logs ou evidências adicionais da execução manual.
