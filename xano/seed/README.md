# Catálogo inicial de animais

`animal-catalog.json` contém duas espécies, 21 raças caninas e 20 felinas.
É uma seleção inicial ampliável, não uma taxonomia completa nem ranking brasileiro.
Não contém IDs remotos. Fontes consultadas em 21/10/2026:

- [AKC, registros de cães de 2025](https://www.akc.org/expert-advice/dog-breeds/most-popular-dog-breeds-2025/): primeiras 20 raças e Shih Tzu (posição 21), já presente no banco.
- [CFA, lista de 2026 baseada no ano anterior](https://cfa.org/cat-talk/most-popular-breeds-for-2026/): dez raças felinas; complementar com as dez raças distintas seguintes do GCCF, em ordem de registros.
- [GCCF, registros de 2025](https://www.gccfcats.org/wp-content/uploads/2026/01/Registered-Cats-By-Breed-2024-2025.pdf): Siamês, Burmês, British Longhair, Oriental de Pelo Curto, Sagrado da Birmânia, Norueguês da Floresta, Tonquinês, Sphynx, Bengal e Somali de Pelo Longo. Categorias de pets sem raça registrada foram excluídas. A categoria ampla Russian não é mapeada para Azul Russo; esta última tem fonte própria CFA.

Os nomes em português são rótulos de apresentação; os nomes das fontes estão no nome ou nos aliases de cada entrada. Aliases são equivalências explícitas restritas à espécie, não regras de aproximação textual. Variedades não são fundidas por tamanho, cor ou semelhança. SRD corresponde a `raca_id` ausente, sem linha artificial.

## Correspondências revisadas

Inventário remoto somente de leitura: workspace 167758, 21/10/2026.

| Registro | Correspondência | Ação |
|---|---|---|
| Cachorro, espécie ID 1 | `cao` | Reutilizar ID e nome |
| Shitzu, raça ID 1, espécie 1 | `cao-shih-tzu`, alias explícito da grafia legada | Reutilizar ID e nome, sem renomear |
| Gato | `gato` | Criar espécie ausente |
| Outras 20 caninas + 20 felinas | Chaves individuais no JSON | Criar apenas ausentes |

Antes: 1 espécie, 1 raça, 3 pets e 1 vínculo veterinário/espécie.
Plano: criar 1 espécie e 40 raças; preservar nomes/IDs e todos os vínculos existentes.

Carga autorizada e concluída em 21/10/2026 no workspace 167758: 2 espécies e 41 raças, sendo 21 caninas e 20 felinas. Conferência posterior por leitura confirmou todas as entradas, ausência de duplicidades e preservação dos registros anteriores. A API pública de opções de cadastro retornou as duas espécies. Ver `openspec/changes/archive/2026-10-21-popular-catalogos-especies-racas/verification.md` para manifestos e limitações dos testes dispensados.

## Operação

Usar o Python de `.venv` e o perfil administrativo Xano, sem credenciais em argumentos ou no repositório. `XANO_CONFIG` seleciona outro arquivo de perfis. O workspace precisa corresponder explicitamente ao perfil. `XANO_TENANT` seleciona ambiente isolado; nunca reutilizar um plano entre ambientes. Não definir o tenant para a carga principal.

```powershell
.venv/Scripts/python.exe scripts/animal_catalog.py --validate
.venv/Scripts/python.exe scripts/animal_catalog.py --profile vetech --workspace 167758
```

O segundo comando apenas lê e salva `plan.json` em `.venv/animal-catalog/<execução>/`. Revisar esse plano antes de aplicar. A aplicação compara novamente ambiente, hash do conjunto, IDs, nomes e hashes das referências; divergências exigem outra simulação.

Publicar primeiro somente os dois schemas de catálogo, após inventariar duplicidades e revisar o dry-run:

```powershell
xano.cmd workspace push -d xano -i table/especie.xs -i table/raca.xs --dry-run
xano.cmd workspace push -d xano -i table/especie.xs -i table/raca.xs
.venv/Scripts/python.exe scripts/animal_catalog.py --profile vetech --workspace 167758 --apply .venv/animal-catalog/<execução>/plan.json
```

As únicas atualizações de registros anteriores são o preenchimento técnico de `nome_normalizado` nos catálogos. Normalização: Unicode NFC, espaços externos removidos/internos colapsados e casefold, preservando acentos. Índices únicos: nome normalizado em espécie e par espécie/nome normalizado em raça. Não existe API pública de escrita dos catálogos; todo escritor administrativo deve usar esta ferramenta. Escrever diretamente no banco sem preencher a chave técnica não faz parte deste contrato.

A API de metadados desta instância atualiza registros por `PUT /workspace/{workspace_id}/table/{table_id}/content/{content_id}`. No preenchimento técnico, a ferramenta envia o registro completo preservando os campos anteriores. O contrato foi conferido no OpenAPI da própria instância em `/apispec:meta?type=json`.

Cada escrita registra intenção antes da requisição e confirmação com ID/hash depois. O manifesto distingue execução completa/incompleta. Falha de rede após escrita é resultado incerto: não repetir o POST; comparar o estado remoto e o campo `pending`, gerar novo plano e retomar apenas ausentes. Uma entrada de resultado incerto não é atribuída ao lote para exclusão automática. HTTP 429 explícito pode ser repetido com espera limitada. Reexecutar um conjunto concluído requer nova simulação e cria zero entradas.

## Reversão restrita

Suspender cadastros/alterações de pets, aptidões e catálogos durante a reversão para impedir que uma referência seja criada entre a checagem e a exclusão administrativa. O comando recusa execução sem confirmação desse estado operacional. Essa pausa não é necessária para a carga aditiva.

```powershell
.venv/Scripts/python.exe scripts/animal_catalog.py --profile vetech --workspace 167758 --rollback .venv/animal-catalog/<execução>/manifest.json --writes-suspended
```

Remove somente IDs confirmados como criados por aquele manifesto e cujo hash continua igual. Raças referenciadas por pets, espécies usadas por pets/raças/aptidões e entradas modificadas são preservadas, com resultado parcial explícito. Registros preexistentes nunca são excluídos nem renomeados. Campos/índices técnicos permanecem após reversão. Ao adicionar nova tabela que referencie catálogo, ampliar a checagem antes de usar a reversão.
