# Design

## Context
attendance_history_dialog é compartilhado entre Atendimento, Horários e Consultas. A leitura existente valida consentimento e audita acesso. O pet retornado atualmente por assert_access omite foto; a agenda pode já tê-la na sessão. pet_summary também é usado por outros fluxos e não será ampliado globalmente.

## Goals / Non-Goals
Reorganizar apresentação como perfil sem alterar fontes, estado clínico, rascunho ou regras de gravação. Não criar recursos sociais, seguidores ou fotos artificiais.

## Decisions
- Componente local de perfil no começo do corpo rolável: retrato à esquerda e nome, cinco contagens e dados ao lado em desktop. Em celular, retrato/nome centralizados, contagens e dados em grade legível.
- Reutilizar consultation_avatar, com patinha vetorial e ocultação ao carregar a imagem. Nome e rótulos acessíveis; moldura decorativa em cor temática, sem selo de validação.
- Somente depois do sucesso autenticado e sob o guard de sessão/geração existente, projetar foto sanitizada do pet. Para contrato antigo, reutilizar foto de agenda/upcoming correspondente ao pet e autorizado na mesma sessão. Não exibir dados de seleção anterior durante loading/falha.
- Adicionar foto à projeção autorizada de assert_access. Sem consulta adicional. Publicação deste campo é necessária para foto em acessos diretos sem cache da agenda; fallback continua honesto.
- Preservar mascote, cores/tema contextual existente, categorias, erros/nova tentativa, Escape, foco e rolagem interna.

## Risks / Trade-offs
Foto antiga em cache → só usar após leitura de histórico confirmar acesso atual. Dados sem unidade → conservar Peso informado sem acrescentar kg. Contrato remoto antigo → fallback permitido ou patinha; registrar publicação pendente sem bloquear tela.

## Migration Plan
Sem migração de tabelas. Publicar assert_access aditivo no Xano para fornecer foto no acesso direto. Rollback somente apresentação/projeção.

O rótulo acima do nome usa “Perfil do pet”, conforme o texto solicitado.
