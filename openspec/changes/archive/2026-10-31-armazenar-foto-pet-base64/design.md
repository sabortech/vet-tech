# Design

## Context

O fluxo anterior usava `rx.upload`, enviava `multipart/form-data` com o arquivo
em `foto` e o endpoint `POST /pets` criava uma imagem privada com
`storage.create_image`. A leitura no front aceitava somente URLs `http(s)://`,
descartando caminhos privados do storage.

## Goals / Non-Goals

**Goals:**

- Persistir a foto como texto base64 na coluna `pet.foto`.
- Exibir a foto persistida sem chamada adicional ao backend.
- Manter o cadastro sem foto funcionando como antes.

**Non-Goals:**

- Migrar fotos já armazenadas como imagem do Xano.
- Redimensionar ou comprimir imagens no front.
- Edição ou remoção de foto de pet existente.

## Decisions

- **Data URI completo em vez de base64 puro.** O front grava
  `data:<content-type>;base64,...`. Assim o valor já é utilizável diretamente em
  `rx.image(src=...)` e preserva o tipo da imagem sem coluna extra. Alternativa
  descartada: base64 puro, que exigiria guardar o content-type separadamente.
- **Conversão no backend do Reflex.** O evento `create_pet` já recebe os bytes via
  `rx.UploadFile`; a conversão com `base64.b64encode` acontece ali, sem script no
  navegador. O cadastro passa a usar sempre `json_payload`.
- **Xano grava o texto sem transformação.** `POST /pets` recebe `text? foto?` e
  grava `foto: $input.foto`. Não há decodificação no Xano.
- **Exibição aceita `data:image/`.** `_pet_photo_url` (perfil) e a projeção do
  dashboard aceitam `https://`, `http://` e `data:image/`. Outros esquemas
  continuam descartados, evitando renderizar valores arbitrários.
- **Limite de 1 MB no upload.** Reduz o tamanho do JSON de cadastro e das
  listagens.

## Risks / Trade-offs

- Listagens maiores, pois cada pet carrega a imagem inteira → limite de 1 MB e,
  no futuro, avaliar miniaturas ou endpoint dedicado à foto.
- Perda das fotos antigas ao trocar a coluna para `text` → aceito pela equipe;
  base atual em desenvolvimento.
- O Xano não valida se o texto é realmente uma imagem → o front só exibe valores
  `data:image/`; validação no backend fica como melhoria futura.
