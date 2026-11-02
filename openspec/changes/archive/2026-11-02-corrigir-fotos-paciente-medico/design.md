# Design

## Context

Ver proposal.md. `agenda_GET.xs` já projeta `pet_foto` com consentimento; `Clinical/assert_access.xs` já projeta `foto`. Os documentos registram publicação pendente, ainda sem confirmação remota. `select_consultation` descarta a foto recebida do histórico. `pet_summary` omite foto e `attendance_patient` sempre usa ícone. O histórico já sanitiza foto e aceita cache autorizado do mesmo pet.

## Goals / Non-Goals

**Goals:** preservar a fotografia cadastrada nas apresentações médicas usando os contratos e componentes existentes, com isolamento entre contextos.

**Non-Goals:** galeria, upload de exames, alteração de armazenamento, migrações ou mudanças em rascunho e publicação clínica.

## Decisions

- Reutilizar `agenda_photo` e `consultation_avatar`; evitar outro sanitizador ou componente. Conferir os formatos já aceitos no cadastro para evitar divergências.
- Incluir foto sanitizada na projeção clínica e priorizar a resposta atual no resumo. Centralizar somente a resolução comum necessária para os três consumidores, sem mover módulos.
- Reutilizar agenda apenas quando a leitura clínica bem-sucedida omite a chave foto, com mesmo pet e autorização explícita. Null/vazio explícito prevalece sobre cache. Preservar base64 em data URI, já usado pelo cadastro. Manter guards de sessão/geração, limpeza e auditoria atuais. Não consultar endpoints do tutor pelo perfil médico.
- Substituir o ícone fixo do paciente por avatar com alternativa neutra, preservando temas, layout responsivo e eventos.
- Conferir o contrato publicado antes de qualquer atualização Xano; preservar filtros de consentimento e publicação de outros recursos. A fonte local não comprova publicação remota.

## Risks / Trade-offs

- Backend sem publicação → validar retorno remoto com dados sintéticos e publicar somente o necessário; registrar bloqueio de acesso se ocorrer.
- Foto antiga ou de outro paciente → testar seleção, sessão, erro, revogação e resposta atrasada.
- Imagem existente inválida ou indisponível → manter sanitização e indicar falha com image-off; patinha só para ausência explícita no banco.

## Migration Plan

Sem migração de dados. Preparar e verificar alterações locais; conferir/publicar contratos aditivos no Xano; validar aplicação com paciente sintético em desktop/celular. Reversão do frontend não apaga fotos ou registros. Não reverter dados ou sobrescrever alterações remotas posteriores.
