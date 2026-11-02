# Design

## Context
Ver proposal.md. A agenda já tem seleção de dia, paginação de 25 itens, proteção por gerações de sessão, ações e consentimento. O endpoint retorna nome e motivo, mas não foto. A sidebar compartilhada contém destinos de tutor; Configurações exige esse perfil.

## Goals / Non-Goals
**Goals:** aproximar a referência usando tokens e componentes existentes; restringir extensões compartilhadas a parâmetros opcionais; verificar regressões de navegação e fluxo clínico.
**Non-Goals:** criar áreas de pacientes/exames, configurações médicas, duração de reserva, encaixe/arrastar consultas, disponibilidade, novas permissões ou alterar atendimento/tutor.

## Decisions
- Estender layout_com_menu com conteúdo opcional de navegação; renderizar os botões médicos com as classes sidebar existentes. Reutilizar toggle, drawer e backdrop evita duplicar comportamento. Menu mantém apenas Horários/Consultas e identidade textual real, sem fotografia profissional fictícia.
- Compor a nova agenda em components/veterinary_schedule.py e manter no módulo clínico os fluxos já existentes. Estado e projeções da agenda permanecem no domínio clinical; CSS com prefixo vet-schedule para isolamento.
- Agrupar por hora, com grid de cards que cresce com o conteúdo; mostrar minutos reais. Expandir faixa para horários fora de 08–17. Não posicionar cards absolutamente nem atribuir duração inexistente.
- Resumo: total do dia, finalizadas e em atendimento na página. Não reproduzir horários livres fictícios do protótipo. Controles de data/semana usam date/timedelta, com rótulos portugueses explícitos.
- Foto é campo opcional aditivo pet_foto na resposta autorizada da agenda; ramo revogado mantém sua projeção mínima atual. Usar base64 já armazenado ou URL retornada, sem novas chamadas de histórico para obter foto. Fallback neutro para ausência/erro.
- Manter paginação e proteção contra respostas atrasadas; bloquear controles durante carregamento para evitar cliques concorrentes. Não alterar tokens globais.

## Risks / Trade-offs
- Foto pode aumentar payload → consultar fotos apenas de pets com consentimento ativo; retornar somente a página de 25 itens e não adicionar requests HTTP por card.
- Resumo parcial → rotular explicitamente indicadores da página.
- Backend remoto sem projeção atualizada → fallback mantém a agenda funcional, registrar separadamente publicação e verificação remotas.
- CSS compartilhado → verificar menu do tutor e compilar todas as páginas.

## Migration Plan
Mudança aditiva na projeção Xano sem migração de banco. Publicar endpoint pelo processo existente quando disponível; rollback remove apenas apresentação e campo aditivo, preservando reservas, fotos, histórico e permissões.
