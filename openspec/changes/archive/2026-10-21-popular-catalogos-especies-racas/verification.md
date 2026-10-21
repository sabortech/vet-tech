# Verificação de popular-catalogos-especies-racas

## Curadoria e inventário — 21/10/2026

Conjunto versionado em `xano/seed/animal-catalog.json`: 2 espécies, 21 raças caninas e 20 felinas. Critérios/fontes/aliases em `xano/seed/README.md`; tabela completa agrupada por espécie em `records.md`. AKC 2025, CFA 2026 e GCCF 2025 são fontes primárias consultadas pela web; a seleção não é apresentada como ranking brasileiro nem como lista completa.

Inventário por GET no workspace 167758: 1 espécie (`Cachorro`, ID 1), 1 raça (`Shitzu`, ID 1, espécie 1), 3 pets e 1 vínculo veterinário/espécie. A grafia legada tem correspondência explícita com Shih Tzu, sem renomear nem substituir IDs. Não foram encontrados conflitos de correspondência ou nomes normalizados duplicados. Nenhum registro artificial SRD é previsto.

Simulação real executada:

```powershell
.venv/Scripts/python.exe scripts/animal_catalog.py --profile vetech --workspace 167758
```

Plano privado: `.venv/animal-catalog/20261021T171002238343Z/plan.json`. Resultado: reutilizar 1 espécie e 1 raça; criar 1 espécie e 40 raças. A ferramenta leu os quatro conjuntos antes/depois e confirmou hashes idênticos: nenhuma escrita de dados. Plano contém somente dados de catálogo e hashes/IDs das referências, sem credenciais ou registros pessoais.

## Implementação e verificações locais

Ferramenta administrativa `scripts/animal_catalog.py`: padrão sem escrita, ambiente/workspace explícitos, revalidação do plano, confirmação dos índices antes de aplicar, backfill só do campo técnico dos catálogos, manifesto por escrita, estado incompleto explícito e retomada por nova simulação. Não repete POST de resultado incerto nem atribui sua propriedade ao lote sem confirmação.

Reversão exige suspensão operacional das escritas de pets/aptidões/catálogos; considera apenas IDs confirmados no manifesto, preservando entradas referenciadas, alteradas ou preexistentes. Contratos e comandos estão no README do conjunto. A ferramenta não oferece endpoint público de escrita.

13 testes locais aprovados por:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests/unit -p test_animal_catalog.py -v
```

Cobertura: nomes vazios, origem ausente, raça sem espécie, SRD artificial, aliases duplicados/ambíguos, duplicidade normalizada, Unicode/espaços/acentos, correspondência legada, simulação sem escrita, alteração de plano/ambiente, reexecução idempotente, disputa simulada no índice único, falha parcial, resposta perdida após escrita e reversão completa/parcial preservando referências. A implementação do cliente confere o formato `fields` observado por GET na API real de índices. Cenários de escrita/concorrência/reversão usam backend em memória; não são evidência de execução integrada remota.

## Dry-run dos schemas

```powershell
xano.cmd workspace push -d xano -i table/especie.xs -i table/raca.xs --dry-run
```

Aceito pelo Xano: 2 tabelas atualizadas, com adição de campo técnico `nome_normalizado` em cada uma; índices únicos definidos no schema local para espécie/nome normalizado. Nenhuma API, tabela alheia, pet ou identidade incluída. Na etapa inicial, somente o dry-run foi executado; a publicação autorizada posteriormente está registrada abaixo.

## Bloqueio da verificação integrada

A conta atual recusou os dois mecanismos de ambiente isolado:

- `xano tenant create ... --type tier1`: HTTP 500, `Data Isolation tenants are not enabled.`
- `xano sandbox get -o json`: `Access Denied. Not supported with Free plan.`

Nenhum tenant foi criado e nenhum sandbox foi disponibilizado. Esse bloqueio interrompeu a primeira etapa; o usuário dispensou posteriormente o ambiente isolado e autorizou carga no workspace existente. Testes autenticados de cadastro com/sem raça, concorrência e reversão remota não foram exercitados e não devem ser inferidos das verificações locais.

O reparo da `.venv` instalou as dependências já definidas em `requirements.txt`, sem adicionar dependência ao projeto. Até o encerramento da primeira etapa, nenhum dado remoto havia sido modificado.

## Publicação direta autorizada — 21/10/2026

O usuário pediu explicitamente subir sem os testes prévios e conferir os registros depois, por não dispor de plano Pro ou outro workspace. Design e tarefas 3.1/3.2 foram ajustados para essa estratégia, preservando a distinção entre verificação de dados e cenários de teste dispensados.

Snapshot privado anterior à publicação: `.venv/animal-catalog/before-publication.json`, com catálogos e referências. O novo dry-run confirmou somente duas tabelas; a publicação transacional padrão da CLI concluiu com `Pushed 2 documents to workspace 167758`. Nenhuma API ou outra tabela foi publicada. Os índices únicos foram confirmados por GET nos metadados.

A primeira tentativa de carga parou no backfill técnico sem criar registros. A API desta instância exige PUT, e não PATCH, para atualizar conteúdo. Esse contrato foi consultado no OpenAPI oficial da instância (`/apispec:meta?type=json`); a ferramenta foi corrigida para enviar o registro completo, preservando os campos anteriores. O manifesto da tentativa incompleta é `.venv/animal-catalog/20261021T172427883418Z/manifest.json`, com zero criações confirmadas.

Após nova simulação por leitura, o plano `.venv/animal-catalog/20261021T172551910665Z/plan.json` confirmou novamente 1 espécie e 40 raças a criar, com 2 registros reutilizados. A carga autorizada foi iniciada com manifesto por escrita em `.venv/animal-catalog/20261021T172601318166Z/manifest.json`.

## Resultado confirmado no workspace principal

A carga concluiu com `state=complete`: 41 novos registros (1 espécie e 40 raças), chegando a 2 espécies e 41 raças. Distribuição confirmada: Cachorro ID 1 com 21 raças e Gato ID 2 com 20. O registro legado `Shitzu` manteve ID 1, nome e espécie originais. Os únicos preenchimentos nos registros anteriores foram as chaves técnicas normalizadas nos dois catálogos.

Conferência independente, somente por leitura, registrada em `.venv/animal-catalog/publication-verification.json`:

- Todas as 43 entradas do conjunto (2 espécies + 41 raças) localizadas uma única vez; zero faltantes e zero duplicidades.
- Todas as raças vinculadas à espécie esperada, com chaves normalizadas válidas.
- Ambos os índices únicos publicados confirmados pela API de metadados.
- Campos anteriores de espécie, raça, 3 pets e 1 vínculo veterinário/espécie coincidem com o snapshot anterior à publicação; IDs preservados.
- `GET /api:H62nB-j2/cadastro/opcoes` retornou HTTP 200; as espécies públicas coincidem integralmente com o catálogo carregado e contêm somente ID/nome.
- Nova simulação `.venv/animal-catalog/20261021T172955515741Z/plan.json` indicou reutilização de 2 espécies e 41 raças, sem qualquer nova entrada a criar. Essa conferência não executou nova carga.

Conjunto SHA-256: `19f8a82c8cb5abe1b8801db2d13ef0a28b244418978eb4ec71603cc7fd3da8cf`. Não foram criadas contas nem pets de teste, nem executados testes autenticados de cadastro ou reversão remota, conforme dispensa expressa do usuário. Nenhum dado de pet ou identidade foi alterado pela carga. O resultado confirma os registros e a consulta pública; não declara testes de fluxos autenticados dispensados.
