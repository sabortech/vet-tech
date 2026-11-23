# Design

## Context

O perfil `clinica_admin` identifica a clínica da sessão. `veterinario.clinica_id` comporta no máximo uma clínica; o helper `Identity/create_veterinario` já valida dados profissionais, reserva de e-mail e catálogos. A listagem administrativa já limita os resultados à clínica autenticada.

## Goals / Non-Goals

**Goals:** reutilizar cadastro e identidade existentes e proteger a associação contra acesso indevido e concorrência.

**Non-Goals:** transferência automática entre clínicas e ampliação de acesso a prontuários.

## Decisions

- A interface apresenta ações separadas e estados de carregamento, erro e sucesso. O backend deriva a clínica do administrador ativo, nunca de um ID fornecido pelo cliente.
- O novo cadastro reutiliza validações e persistência existentes, inclusive unicidade e boas-vindas. A clínica fornece senha provisória; o profissional usa as configurações existentes para alterá-la. A senha não deve ser registrada em logs ou armazenada em texto puro.
- O vínculo usa identificador profissional e revalida atomicamente a ausência de clínica; solicitações concorrentes não podem sobrescrever o vínculo vencedor. Não permitir transferência de conta já vinculada.
- Para uma conta existente, a clínica envia um convite e o profissional aceita autenticado; o vínculo só é efetivado na aceitação, depois de nova verificação de disponibilidade. Para novo cadastro, o vínculo é criado diretamente com a conta e a senha provisória informada pela clínica.

## Risks / Trade-offs

- [Associação de conta alheia] → Exigir aceitação do profissional e prova de identidade apropriada.
- [Concorrência entre clínicas] → Garantir operação atômica no Xano e testar duas solicitações simultâneas.
- [Ambiente remoto] → Publicar e validar em Xano isolado antes de disponibilizar.
