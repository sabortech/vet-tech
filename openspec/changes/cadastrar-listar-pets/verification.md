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
