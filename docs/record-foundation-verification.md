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

## Identidade com dois perfis

Por autorização para resolver as decisões e continuar, adotou-se e-mail único
**dentro de cada tabela de domínio**, permitindo a mesma pessoa/e-mail nos dois
perfis. Não foi criada tabela `user` ou uma terceira identidade. A decisão
preserva os cadastros existentes e não mescla contas por coincidência de e-mail.

`POST Authentication/profiles/login` valida separadamente `tutor.password` e
`veterinario.senha`, e retorna `profiles`, cada item com `perfil`, `id` e
`authToken` próprio. Só são retornados perfis cuja senha foi comprovada. Se as
senhas diferirem, a credencial informada autentica somente seu perfil; se forem
iguais, retorna ambos, sem escolher silenciosamente o primeiro. Não há migração
ou sincronização automática de senhas. A futura `unificar-acesso-perfis` usará
essa resposta na interface compartilhada; o login atual de tutor continua válido.

O schema remoto já torna `veterinario` autenticável; são preservados os índices
únicos de e-mail e do par `crmv_uf`/`crmv`.
O nome legado `cmv` foi preservado para não renomear dados sem migração; representa
CRMV. Cadastro profissional, validação de habilitação, especialidades e clínica
continuam pertencendo à futura change de identidade. Um usuário da aplicação
não pode criar seu próprio registro profissional por este contrato.

## Preparo do Xano de desenvolvimento

Não publicar diretamente em uma base com dados existentes. Executar primeiro
o inventário e a reconciliação descritos em `backend-foundation.md`. Em especial:

1. Identificar vínculos nulos/órfãos e e-mails/CRMV duplicados; resolver com fonte
   confiável antes de ativar obrigatoriedade e índices únicos.
2. Preservar uma cópia dos logs antigos com sua data e precisão originais. A
   conversão de `date` em `timestamp` não recupera horários. Logs sem fonte de
   horário devem permanecer no acervo legado identificado; não inventar meia-noite
   como horário real. A tabela de operações novas exige timestamp com hora.
3. Importar tabelas, funções e endpoints em uma cópia isolada de desenvolvimento,
   sem apagar histórico. Conferir autenticação veterinária por `senha`, ausência
   de CRUD público de logs e rollback de transações antes de liberar usuários.
4. Criar somente fixtures sintéticas: dois tutores, dois veterinários, pet A do
   tutor A, pet B do tutor B, consulta de B, duas espécies e raça da outra espécie.
   Reservar um ID positivo inexistente para os testes negativos.
5. Tutor A e veterinário A devem compartilhar o e-mail fictício e a senha de
   teste; criar tokens por tabela. A senha de teste não é uma senha de usuário real.

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
  "dual_email": "fixture-foundation@example.invalid",
  "dual_password": "CONFIGURAR-SENHA-SINTETICA"
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

A suíte remota verifica identidade dupla, invariantes de pets, consulta e exame,
consentimento individual, dois veterinários, outro tutor/pet, autoria forjada,
logs por operação, adulteração e revogação com os mesmos tokens. Qualquer falha
encerra com código diferente de zero; ausência de configuração não é sucesso.

Para a falha real de auditoria, exclusivamente na cópia isolada, salvar a função
`records/audit` e temporariamente fazê-la lançar um erro antes da inserção do log.
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
rollback ou permissões remotas. Nenhuma execução remota foi realizada nesta sessão
porque não há perfil Xano nem arquivo de fixtures configurado.

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
identidade (`acesso/login` e reserva de e-mail) foi identificada como diferente
da proposta local de `profiles/login`; ambas precisam ser reconciliadas antes
de publicar um segundo contrato de login. Não foi alterada a política remota.

Ainda não houve push ou integração. Foi solicitada confirmação de que o
workspace configurado é o ambiente de desenvolvimento, pois há apenas a branch
ativa e não é possível criar ambiente separado com as permissões atuais.
