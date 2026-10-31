# Proposal

## Why

O cadastro de pet enviava a foto como arquivo multipart e o Xano a gravava em uma
coluna `image` via `storage.create_image`. A equipe decidiu simplificar o fluxo:
o front converte a imagem em base64 e o Xano grava o texto diretamente na coluna
`foto`, sem depender do storage de arquivos do Xano.

## What Changes

- O front lê o arquivo selecionado no upload e o envia no JSON do cadastro como
  data URI (`data:<content-type>;base64,<conteúdo>`) no campo `foto`; o envio
  multipart deixa de ser usado no cadastro de pet.
- O limite de tamanho da foto no upload cai de 5 MB para 1 MB, porque o base64
  aumenta o payload em cerca de 33% e a foto passa a trafegar em todas as
  listagens de pets.
- A lista de pets e o dashboard do tutor passam a exibir fotos em data URI
  `data:image/...`, além das URLs `http(s)://` já aceitas.
- **BREAKING (dados)**: a coluna `pet.foto` muda de `image` para `text`, e o input
  `foto` de `POST /pets` muda de `file` para `text`. Fotos já armazenadas como
  imagem do Xano deixam de ser exibidas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `pet-management`: formato de armazenamento e retorno da foto do pet.
- `tutor-profile-presentation`: contrato de envio da foto no formulário de cadastro.

## Impact

- Front: `vet_tech/features/auth/state.py`, `vet_tech/features/dashboard/state.py`,
  `vet_tech/components/pets.py` e `tests/unit/test_auth_state.py`.
- Xano: `xano/table/pet.xs` e `xano/api/pet/pets_POST.xs`. `pets_GET` e os
  dashboards já retornam o campo `foto` sem alteração.
- Dados sensíveis: a foto do pet não faz parte do prontuário nem é dado pessoal do
  tutor; não há impacto em auditoria. A foto continua protegida pelos mesmos
  filtros de propriedade das leituras de pet, mas deixa de usar acesso privado do
  storage: quem lê o registro recebe a imagem completa embutida.
- Autorização: sem mudança; o cadastro continua exigindo tutor autenticado e
  associa o pet a `$auth.id`.
- Notificações: não se aplica.
- Desempenho: respostas de listagem crescem proporcionalmente ao número de pets
  com foto; o limite de 1 MB por imagem mitiga o impacto.
