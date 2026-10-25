# Verificação de selecionar-alternar-pet

## Contrato implementado

`GET /api:vettech-pets/pets/{pet_id}` exige autenticação `tutor` e filtra
simultaneamente `pet.id` e `pet.tutor_id` pela identidade autenticada. Retorna
somente dados cadastrais básicos; não inclui tutor, credenciais ou arquivo privado.

Respostas previstas: 200 para pet próprio, 400 para ID inteiro não positivo, 401 para
autenticação ausente/inválida e 404 genérico para pet alheio ou inexistente.
As respostas reais serão registradas após a execução integrada.

Na primeira execução, o teste detectou que o roteador Xano responde 404 para
ID não numérico antes de entrar no endpoint. O design e o teste foram ajustados
para esse comportamento, mantendo a rejeição sem dados exigida pela spec.
As fixtures dessa execução foram removidas e os registros anteriores ficaram
inalterados, conforme a comparação dos hashes dos registros.

O dry-run do Xano aceitou o script e mostrou somente um endpoint a criar.
Não há alteração de tabelas ou migração de registros.

## Cliente HTTP

`XanoRequestError` preserva a mensagem e acrescenta `status_code` opcional.
Os três testes de compatibilidade, status 401/404/503 e timeout passaram.

## Contexto para extensões clínicas futuras

`selected_pet_id` é derivado somente do objeto autorizado, nunca do ID pendente.
`_clear_pet_context()` centraliza a invalidação; gerações de sessão e seleção
impedem aceitar respostas de outro contexto. Novos dados de consulta/vacina/
prescrição deverão se vincular ao ID validado e participar dessa limpeza.
Nenhum módulo clínico foi implementado nesta change.

## Verificações intermediárias

- Publicado somente o novo endpoint (1 documento) após dry-run; GUID atribuído pelo Xano.
- Suíte local: 30 testes aprovados, incluindo invalidação de respostas antigas,
  falha de catálogo, status HTTP, recuperação e limpeza de sessão.
- Primeira compilação do Reflex aprovada.
- API real: 9 cenários de autorização/respostas passaram; o fluxo de estado
  foi verificado separadamente após a janela de requisições do plano.

## Integração real concluída

`run_pet_selection_live.py --allow-temporary-records --keep-fixtures` passou:

- 9 cenários HTTP: pets próprios 200, pets alheios/inexistentes 404 genérico,
  ID zero 400, ID não numérico 404 do roteador, token ausente/inválido 401.
- O estado Reflex fez chamadas reais ao Xano com três contas sintéticas: dois
  pets em uma conta, um em outra e nenhum na terceira. Abertura/alternância,
  negativa de pet alheio, ausência de seleção automática e logout passaram.
- Comparação dos hashes dos registros anteriores confirmou que permaneceram
  inalterados. As fixtures desta execução foram mantidas apenas para a QA visual
  e serão removidas ao concluir a verificação.
- Foi necessário espaçar os percursos independentes para respeitar a janela
  de requisições do plano Xano; as respostas não foram simuladas.

## Interface e encerramento da verificação

`run_pet_selection_browser.py` passou usando Chrome headless e a aplicação
Reflex local em modo produção, sem mocks de resposta:

- Desktop 1280×900: abertura por teclado (foco + Enter), dados do pet e SRD.
- Erro real de autorização após transferir temporariamente apenas o segundo
  pet sintético para a outra conta: detalhes anteriores ausentes, mensagem
  genérica e nova tentativa bem-sucedida após restaurar o vínculo.
- A restauração foi comparada ao objeto original para confirmar que nenhum
  campo da fixture foi alterado além da transferência temporária.
- Celular 390×844: alternância, retorno à lista e logout; sem overflow horizontal.
- Outra conta com um pet não herdou seleção nem pets anteriores; conta sem
  pets exibiu lista vazia e manteve o cadastro acessível.
- Nenhum erro JavaScript detectado. Capturas desktop/mobile/falha/vazio em
  `.venv/pet-selection-qa/` foram geradas; desktop e mobile foram inspecionadas.

Os runtimes integrados de navegador falharam ao inicializar o kernel; a
verificação utilizou Playwright instalado somente no ambiente virtual de teste
e o Chrome já existente. A aplicação não ganhou essa dependência de runtime.

Verificações finais:

- `./.venv/Scripts/python.exe -m unittest discover -s tests/unit -v`: 30 testes aprovados.
- `./.venv/Scripts/reflex.exe compile --dry`: compilação aprovada.
- `openspec validate selecionar-alternar-pet --type change --strict`: aprovado.
- `run_pet_selection_live.py --allow-temporary-records --cleanup`: fixtures
  removidas; hashes de todos os registros preexistentes de tutor/pet permaneceram
  iguais. O arquivo local de credenciais sintéticas também foi removido.

As 9 tarefas foram concluídas e o usuário aprovou o arquivamento. O delta
foi sincronizado com `pet-management` (5 requisitos adicionados e 1 modificado),
preservando o título, Purpose e requisitos não afetados. As três specs principais
passaram na validação do OpenSpec. A change foi arquivada em
`openspec/changes/archive/2026-10-14-selecionar-alternar-pet/`.
