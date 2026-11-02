# Design

## Context
A sidebar médica compartilha veterinary_actions entre Horários, Consultas e Configurações. A sessão mantém nome, mas veterinario/me não retorna CRMV. O endpoint autenticado veterinario/account já retorna crmv/crmv_uf com fallback legado; não é necessário publicar backend.

## Goals / Non-Goals
Melhorar identidade e leitura sem mudar destinos, autenticação ou guard de configurações. Não inventar registros, foto ou validação externa do CRMV.

## Decisions
- Carregar apenas metadados CRMV/UF via evento background na montagem do card, uma vez por sessão confirmada. Liberar lock durante HTTP, descartar resposta de token/perfil/identidade/geração antigos e limpar tudo na saída. Tutor não solicita essa leitura.
- Configurações atualiza os mesmos metadados após sua leitura autenticada confirmada, reaproveitando dados já recebidos. Nome segue identity_name atualizado pelo fluxo existente.
- Loading/ausência/falha explícitos; falha permite nova tentativa local. Não bloquear navegação ou logout durante a leitura.
- Avatar com iniciais derivadas do nome, detalhe de estetoscópio, rótulo “Veterinário(a)” e área de registro com ícone. Usar superfícies e verdes existentes, borda suave, tipografia clara e watermark decorativa sem interceptar cliques.
- Versão compacta mostra avatar e logout acessível, oculta registro/textos. Drawer móvel conserva card expandido. Sem LED novo.

## Risks / Trade-offs
Leitura adicional inicial → cache por sessão e reaproveitamento de Configurações. Nome longo → quebra de linha e min-width 0. Dados ausentes → não informado, nunca valor de exemplo.

## Migration Plan
Sem migração ou publicação de endpoint. Reverter apenas estado/componente/CSS se necessário.
