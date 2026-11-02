# Agenda médica e assistente virtual

## O que mudou

- Agenda do médico remodelada com calendário, navegação por dia, indicadores e cartões de consultas com foto quando disponível.
- Menu médico compartilhado com Horários, Consultas e Configurações; destaque da aba ativa legível nos temas claro e escuro.
- Configurações para o médico com conta, segurança e preferências. Nome e telefone editáveis; e-mail e CRMV/UF somente leitura.
- Calendário com seleção de mês/ano, tartaruga decorativa e borda verde animada.
- Chat global acompanha o tema do usuário, com borda verde animada e vídeo da tartaruga fixo abaixo do cabeçalho, silencioso e em loop.
- Chat acima da mascote, com fundo escurecido e transições suaves de abertura e fechamento. A mascote permanece clicável.

## Como conferir

1. Entre como médico e navegue entre Horários, Consultas e Configurações.
2. Selecione datas pelo calendário e confira os cartões da agenda.
3. Alterne o tema e confira o destaque do menu e o chat.
4. Abra o assistente: confira o vídeo, a posição acima da mascote e o fundo escuro. Feche pelo botão, mascote, Escape ou clique no fundo.
5. Repita a navegação e a abertura do assistente em uma tela de celular e com perfil de tutor.

## Validação

Testes unitários com `python -m unittest discover -s tests/unit -q` (Node no PATH), build de produção Reflex e verificações de navegador em desktop/celular. Evidências por mudança em `openspec/changes/archive/2026-11-*/` e `2026-11-02-*/`.

## Backend

Os três novos endpoints de configurações do médico foram publicados e verificados com contas sintéticas: `GET/PATCH veterinario/account` e `POST veterinario/password`.

O contrato aditivo de foto em `xano/api/clinical/agenda_GET.xs` está versionado, mas ainda precisa de publicação no Xano para retornar `pet_foto`. A interface mantém imagem neutra quando o campo não existe. O merge do GitHub não publica endpoints Xano automaticamente.

As permissões clínicas continuam no backend; dados do pet são retornados apenas com consentimento ativo. Não há migração de tabelas ou nova integração de IA nesta entrega.
