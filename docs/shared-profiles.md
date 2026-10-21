# Acesso compartilhado e navegação

Implementação da change `unificar-acesso-perfis`; consultar seu `verification.md`
para distinguir código local de contratos efetivamente publicados.

## Cadastro e login

`/cadastro` permite escolher Tutor ou Veterinário, preservando o CPF validado do
tutor. Veterinário informa nome, e-mail, telefone, senha/confirmar senha, CRMV/UF,
uma ou mais espécies e especialidades. Clínica é opcional e deve existir quando
informada; esta entrega não cadastra clínicas. CRMV aceita 1–20 caracteres ASCII
alfanuméricos sem espaços internos, normalizados para maiúsculas. A combinação
CRMV/UF é única. Validação de formato não comprova habilitação profissional.

Um e-mail normalizado só pode pertencer a um perfil. `/login` recebe somente
e-mail/senha; `POST /acesso/login` no grupo Authentication retorna `authToken`,
`perfil` e `identidade_id`. O frontend confirma essa identidade em `tutor/me` ou
`veterinario/me`, protegidos pela tabela correspondente, antes de estabelecer a
sessão. IDs iguais nas duas tabelas não representam a mesma pessoa.

`tutor/login` preserva seu contrato legado. `tutor/signup` e
`veterinario/signup` criam reservas únicas de e-mail e identidade dentro da mesma
transação. Falha não pode deixar reserva ou vínculos órfãos. A tabela técnica
`reserva_email` não contém senhas, não autentica e não concede autorização.

`cadastro/opcoes` é público e projeta apenas ID/nome de catálogos e clínicas;
não substitui os endpoints de catálogo protegidos de tutor. Especialidades
iniciais estão em `xano/seed/especialidades.json`; espécies/raças serão ampliadas
pela change de carga própria, sem listas fictícias na interface.

## Navegação e extensões

`pages/profile.py` compõe as áreas dos perfis. `components/navigation.py`
contém menu e modal reutilizáveis; `components/pets.py` mantém os componentes
do cadastro, detalhes e lista. A única sessão permanece no estado de autenticação.

Menu tutor: Início, Vacinas, Medicamentos, Doenças e Consultas; Novo pet e Mudar
pet no rodapé. O nome do pet e a seção ativa devem permanecer claros. Recolher
o menu não altera o animal. O modal reutiliza cadastro e API existentes; fechar
sem enviar limpa o rascunho. Enquanto envia, o fechamento é recusado; sucesso
atualiza a lista sem selecionar automaticamente o animal novo. Mudar pet
reutiliza a consulta autorizada e a limpeza por gerações de sessão/contexto.

Novas capacidades clínicas devem participar de `_clear_pet_context()` e
revalidar geração de sessão, contexto e token ao receber respostas. Não usar
pet pendente como autorização. A área veterinária desta entrega só identifica
a sessão; seções clínicas exibem indisponibilidade até suas próprias entregas.

## Inventário, implantação e reversão

Executar `.venv/Scripts/python.exe scripts/profile_migration_inventory.py` para
inventário remoto somente de leitura. O resumo apresenta contagens; snapshot
com dados pessoais e hashes fica exclusivamente em `.venv/profile-migration/`,
ignorado pelo Git. `--snapshot <arquivo>` refaz a análise local sem rede.

Antes da implantação: simular em ambiente isolado, confirmar preservação dos
registros e testar concorrência/rollback. Suspender cadastros durante backfill,
repetir inventário e bloquear se houver conflitos. Criar os índices e reservas
sem alterar IDs, senhas ou vínculos de pets; publicar o frontend somente após
os novos endpoints estarem verificados. Restaurar apenas de backup privado
verificado, sem truncar tabelas ou reprocessar hashes. Um rollback não pode
reativar cadastro legado que ignore a reserva: manter escrita suspensa até
reconciliar identidades criadas. Ver o design da change para a sequência completa.

`scripts/profile_migration_backfill.py --prepare-freeze` gera o bundle de suspensão
em `.venv/shared-profile-migration-frozen/`. Depois do dry-run/publicação desse
bundle, `--snapshot <snapshot.json>` simula as reservas e especialidades, e
`--snapshot <snapshot.json> --apply` aplica somente entradas ausentes. A aplicação
confere a suspensão na função publicada e recusa divergências do snapshot. O
manifesto registra IDs novos e preservação dos digests. Reabrir publicando apenas
`function/identity/check_email_available.xs` do diretório autoritativo `xano/`.

Para QA isolada, `XANO_TENANT` seleciona o tenant no cliente HTTP; remover essa
variável ao usar o backend principal. O servidor local de revisão utiliza a porta
8011. Nunca copiar as rotas privadas de fixtures em `.venv/` para `xano/`.
