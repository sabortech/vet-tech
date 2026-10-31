# Tasks

## 1. Front

- [x] 1.1 Converter a foto selecionada em data URI base64 no evento `create_pet` e enviar o cadastro sempre como JSON.
- [x] 1.2 Aceitar fotos `data:image/` na lista de pets do perfil e no dashboard do tutor.
- [x] 1.3 Reduzir o limite do upload de foto para 1 MB.

## 2. Xano

- [x] 2.1 Alterar a coluna `pet.foto` de `image` para `text` em `xano/table/pet.xs`.
- [x] 2.2 Alterar o input `foto` de `POST /pets` para `text` e gravá-lo diretamente, removendo `storage.create_image`.
- [ ] 2.3 Publicar tabela e endpoint no workspace Xano.

## 3. Verificação

- [x] 3.1 Atualizar testes unitários: cadastro com foto envia data URI em JSON; lista exibe foto base64.
- [x] 3.2 Executar `tests/unit/test_auth_state.py` e `tests/unit/test_dashboard.py`.
- [ ] 3.3 Cadastrar um pet com foto no app local contra o Xano publicado e confirmar a exibição no perfil e no dashboard.
- [ ] 3.4 Sincronizar specs e arquivar a change.
