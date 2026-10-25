# Verificação da fundação clínica

## Contrato implementado nos artefatos locais

Grupo `vettech-records`, com tokens Xano de tabelas de domínio distintas:

| Método e caminho | Token | Resultado |
|---|---|---|
| `PUT /authorizations` | tutor | Dono define `ativo`/`revogado` para pet/veterinário |
| `GET /authorizations?pet_id=` | tutor | Dono consulta consentimentos |
| `GET /audit?pet_id=` | tutor | Dono consulta logs imutáveis |
| `GET /records/tutor?pet_id=` | tutor | Dono consulta o histórico do próprio pet |
| `GET /records?pet_id=` | veterinário | Consultas/exames, consentimento atual e um log |
| `GET /records/export?pet_id=` | veterinário | Mesmo histórico em JSON e log de exportação; sem PDF |
| `POST /consultations` | veterinário | Pet existente, autor autenticado e um log |
| `POST /exams` | veterinário | Pet existente, consulta opcional do mesmo pet e um log |
| `PATCH`, `DELETE /audit/{log_id}` | veterinário | Negativa explícita sem modificar o log |

Exame avulso usa `consulta_id` ausente ou `null` na entrada. O tableref opcional
do Xano pode retornar `0` para ausência de associação; isso não referencia uma
consulta existente. O teste aceita essa representação, mantendo a validação
de consulta existente e do mesmo pet quando um ID é informado.

Tokens de tutor são rejeitados nos endpoints veterinários e vice-versa, mesmo
quando os IDs numéricos coincidem. Não há endpoint público de escrita genérica
nas tabelas. Credenciais da Meta API são administrativas e jamais devem ser
entregues à aplicação ou aos usuários. Conferir também no workspace remoto
que não existem endpoints gerados de CRUD para `log_acesso`.

`records/require_access` reconsulta o consentimento por pet e veterinário em cada
operação. Nenhuma informação de clínica ou perfil enviada pelo cliente concede
acesso. As escritas clínicas e a auditoria estão na mesma `db.transaction`;
falhas não são capturadas nem convertidas em sucesso. Chamadas iniciadas depois
da resposta da revogação devem falhar com o mesmo token anterior. Operações já
em andamento precisam de ensaio concorrente no Xano para aferir seu isolamento.

## Identidade com e-mail único entre perfis

A decisão atual, confirmada pelo usuário, preserva o Xano: `reserva_email` impede
que um e-mail pertença a tutor e veterinário simultaneamente.
`POST Authentication/acesso/login` valida senha, reserva e identidade de domínio,
retornando `authToken`, `perfil` e `identidade_id`. Nenhum perfil enviado pelo
cliente concede privilégios. O login específico de tutor permanece compatível.
Não existe nova publicação de `profiles/login`; sua proposta anterior foi substituída.
São preservados os índices de e-mail e CRMV/UF já publicados. Cadastro profissional,
espécies, especialidades e telas compartilhadas continuam no roadmap específico.

## Preparo do Xano de desenvolvimento

Antes de publicar em desenvolvimento com dados existentes, executar primeiro
o inventário e a reconciliação descritos em `backend-foundation.md`. Em especial:

1. Identificar vínculos nulos/órfãos e e-mails/CRMV duplicados; resolver com fonte
   confiável antes de ativar obrigatoriedade e índices únicos.
2. Preservar uma cópia dos logs antigos com sua data e precisão originais. A
   conversão de `date` em `timestamp` não recupera horários. Logs sem fonte de
   horário devem permanecer no acervo legado identificado; não inventar meia-noite
   como horário real. A tabela de operações novas exige timestamp com hora.
3. Importar tabelas, funções e endpoints em um workspace confirmado de desenvolvimento, com fixtures isoladas,
   sem apagar histórico. Conferir autenticação veterinária por `senha`, ausência
   de CRUD público de logs e rollback de transações antes de liberar usuários.
4. Criar somente fixtures sintéticas: dois tutores, dois veterinários, pet A do
   tutor A, pet B do tutor B, consulta de B, duas espécies e raça da outra espécie.
   Reservar um ID positivo inexistente para os testes negativos.
5. Criar e-mails fictícios distintos para cada identidade e tokens por tabela.
   Senhas e tokens sintéticos ficam somente no arquivo ignorado de fixtures.

Guardar a configuração em `.env.foundation-fixtures.json`, ignorado pelo Git:

```json
{
  "environment": "development",
  "synthetic": true,
  "origin": "https://SEU-XANO-DE-DESENVOLVIMENTO.example.invalid",
  "data_source": "test",
  "tokens": {"tutor_a": "CONFIGURAR", "tutor_b": "CONFIGURAR", "vet_a": "CONFIGURAR", "vet_b": "CONFIGURAR"},
  "tutor_a": 1,
  "tutor_b": 2,
  "veterinario_a": 1,
  "veterinario_b": 2,
  "pet_a": 1,
  "pet_b": 2,
  "consulta_other_pet": 1,
  "especie_a": 1,
  "raca_other_species": 2,
  "missing_id": 2147483647,
  "identity_credentials": {
    "tutor_a": {"email": "tutor-fixture@example.invalid", "password": "CONFIGURAR"},
    "vet_a": {"email": "vet-fixture@example.invalid", "password": "CONFIGURAR"}
  }
}
```

Substituir IDs pelos efetivamente criados. `data_source` é opcional quando a
cópia de desenvolvimento já tem isolamento de workspace. O script exige a
declaração de ambiente de desenvolvimento, usa HTTPS, não busca configuração
produtiva e não imprime tokens ou respostas clínicas.

## Comandos reproduzíveis

```bash
.venv/bin/python -m unittest discover -s tests/unit
.venv/bin/reflex compile --dry
openspec validate --all --strict
git diff --check
.venv/bin/python tests/integration/run_record_foundation_live.py --fixtures .env.foundation-fixtures.json
```

Para verificar também ausência de atores por chamadas diretas, sem invalidar
contas existentes:

```bash
.venv/bin/python tests/integration/run_record_foundation_live.py --fixtures .env.foundation-fixtures.json --phase identity-negative
```

Para repetir o bloco de imutabilidade, histórico existente e revogação depois
de uma correção localizada, reutilizando os mesmos cenários da fase normal:

```bash
.venv/bin/python tests/integration/run_record_foundation_live.py --fixtures .env.foundation-fixtures.json --phase access-regression
```

A suíte remota verifica identidade por domínio e e-mail único, invariantes de pets, consulta e exame,
consentimento individual, dois veterinários, outro tutor/pet, autoria forjada,
logs por operação, adulteração e revogação com os mesmos tokens. Qualquer falha
encerra com código diferente de zero; ausência de configuração não é sucesso.

Para a falha real de auditoria, exclusivamente no desenvolvimento confirmado,
salvar a função `records/audit` e temporariamente fazê-la lançar um erro antes
da inserção do log, limitado ao ID do pet sintético das fixtures.
Não adicionar flag ou bypass ao endpoint público. Executar:

```bash
.venv/bin/python tests/integration/run_record_foundation_live.py --fixtures .env.foundation-fixtures.json --phase audit-failure
```

Essa fase compara o histórico pelo endpoint do tutor antes/depois, exige falha
de leitura/exportação/escrita veterinária e confere ausência de escrita parcial
e de logs de sucesso. Restaurar a função original e repetir a fase normal.
O teste de falha só é evidência quando ambas as fases forem registradas no Xano.

## Preservação e encerramento

Os testes revogam as autorizações criadas em `finally`. Não removem consultas,
exames ou logs: são evidências imutáveis, inclusive em desenvolvimento. Os nomes
clínicos recebem prefixo `fixture-foundation-` único por execução. Manter o
dataset isolado e arquivar seus resultados; descartar a cópia descartável inteira
somente conforme a política de ambientes, sem usar exclusão de logs na aplicação.

A validação sintática local não comprova autenticação, isolamento de tabelas,
rollback ou permissões remotas. As evidências de execução remota ficam em `verification.md` na change;
a preparação histórica abaixo não substitui os resultados da execução atual.

## Reconciliação com o workspace configurado em 2026-10-21

O acesso ao perfil CLI foi confirmado. O pull leu 75 artefatos remotos, que
incluem funcionalidades posteriores ao planejamento local: agenda, rascunhos,
CRMV por UF, `ocorrido_em` e bloqueio por pet. O plano gratuito recusou sandbox
e a criação de outro workspace. A branch disponível é somente `v1` ativa.

A primeira prévia detectou remoções de campos. Ela não foi aplicada. Os schemas
locais de consulta, exame, consentimento, raça, veterinário e log foram
reconciliados para preservar todos os campos e índices remotos. `data_hora` passa
a timestamp com valor padrão para novos logs, preservando também `ocorrido_em`.

O inventário por Meta API encontrou 0 consultas, 0 exames, 0 consentimentos e
0 logs; 3 pets, 3 tutores, 1 veterinário, 2 espécies e 41 raças. Todos os pets
têm tutor/espécie e todas as raças têm espécie na amostra integral inventariada.
Nenhum registro pessoal foi impresso ou alterado nesse inventário.

As novas leituras retornam somente consultas finalizadas ou legadas sem status,
com lista explícita de campos públicos e exames vinculados às consultas
visíveis. Não expõem rascunhos internos pelo endpoint adicional de histórico.
Os endpoints novos com transação usam o mesmo `clinical_lock` por pet dos
endpoints remotos. A auditoria nova preenche `data_hora` e `ocorrido_em`.

A publicação deve ser limitada aos arquivos reconciliados desta change: não
executar push integral de schemas locais antigos ou sobrescrever os endpoints
remotos de cadastro/login, agenda e finalização clínica. A política remota de
identidade (`acesso/login` e reserva de e-mail) foi preservada por decisão do
usuário; a proposta local alternativa `profiles/login` foi retirada.

Naquele inventário ainda não havia push ou integração. A confirmação solicitada
do ambiente de desenvolvimento e da política de identidade foi recebida na
continuação descrita abaixo.

## Autorização de continuidade

O usuário confirmou que o workspace é de desenvolvimento e pode receber as
alterações e os testes sintéticos. Autorizou também preservar e-mail único entre
perfis. Isso resolve as duas pendências descritas no inventário anterior.

A migração aplicada usa os horários confiáveis de `ocorrido_em` para os 9 logs
preexistentes cujo `data_hora` estava vazio. Primeiro o campo foi convertido
para timestamp opcional; os valores foram preenchidos e comparados com a cópia
anterior; depois passou a timestamp obrigatório com padrão para novos logs.
Nenhum horário foi inventado ou registro histórico excluído. A função existente
`Clinical/audit` também grava o novo campo, preservando os demais dados.

O intervalo padrão de 2,2 segundos no harness evita rajadas de requisições;
HTTP 429 continua sendo falha explícita, sem repetir credenciais automaticamente.
As quatro identidades e os pets clínicos sintéticos permanecem em desenvolvimento
como evidência, com autorizações revogadas. Os registros de usuários anteriores
são comparados sem imprimir seus conteúdos.
