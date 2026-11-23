# Design

## Context

`clinica` não autentica, `veterinario.clinica_id` é opcional e `pet.tutor_id` é obrigatório. A adoção existente transfere propriedade em transação e ainda aguarda validação em Xano isolado. As leituras clínicas dependem de propriedade ou autorização veterinária, não de vínculo com clínica.

## Goals / Non-Goals

**Goals:** isolar operações por clínica, manter continuidade dos dados e preservar o contrato de adoção para tutores.

**Non-Goals:** cadastro público de administradores, gestão de vínculos veterinários, acesso clínico da clínica, anúncio de pets já pertencentes a tutor pela nova interface e notificações.

## Decisions

### Identidade administrativa própria

Criar identidade autenticável individual com vínculo obrigatório à clínica e estado ativo; provisionamento confiável pela equipe da plataforma. Derivar clínica do usuário no backend e revalidar em cada operação. A tabela de clínica não vira conta compartilhada: identidades individuais permitem revogação e auditoria. Senhas usam mecanismo seguro existente e não entram em código ou logs. Conta solicitada é criada apenas em ambiente de teste isolado com credencial fornecida fora dos arquivos versionados; a senha indicada pelo usuário é exclusivamente demonstrativa.

O acesso usa a mesma página, formulário de e-mail e senha e operação `acesso/login` existentes para tutor e veterinário. O backend identifica o perfil pela conta autenticada e a aplicação encaminha cada perfil à sua área; não há página de login separada nem seletor de perfil. A identidade interna da clínica existe somente para aplicar as permissões correspondentes.

### Responsabilidade exclusiva

Adicionar vínculo opcional de clínica ao pet e permitir `tutor_id` ausente apenas quando há clínica responsável; validar exclusividade no backend e na integridade do banco quando suportado. Não criar tutor fictício para representar clínica, pois mascararia identidade e permissões. Migrar sem alterar vínculos existentes; revisar todas as consultas que pressupõem tutor obrigatório e garantir negação quando não há proprietário tutor.

Na validação no workspace de desenvolvimento, o Xano gravou `0` ao receber `null` em `tutor_id`. O código deve tratar tanto `null` quanto `0` como ausência de vínculo e exigir IDs positivos para responsáveis; isso não representa um tutor fictício. A integridade e a transferência devem ser verificadas no backend com a representação efetivamente persistida.

### Divulgação e transferência

O cadastro administrativo cria apenas pet novo indisponível; publicação explícita usa clínica derivada da sessão. O endpoint agregado de adoção mantém projeção mínima existente. A transferência atômica usa a mesma trava por pet das operações clínicas, revalida disponibilidade e responsável, remove vínculo de clínica, atribui tutor autenticado e revoga autorizações anteriores. Publicação, retirada e adoção concorrentes devem respeitar a mesma serialização; nenhum cliente pode escolher responsável. Preservar histórico e auditabilidade sem inventar ator veterinário.

### Interface e auditoria

Adicionar área da clínica com lista de veterinários e cadastro/lista de seus pets, com estados de erro e confirmação de publicação/retirada. Reutilizar Adoção no menu do tutor ao lado das áreas do painel, sem duplicar rota. Registrar eventos administrativos imutáveis na mesma transação da alteração; não expor prontuário completo pela área administrativa.

A área da clínica usa a área veterinária existente como referência visual: mesma paleta, sidebar, cartões, tipografia e comportamento responsivo, reutilizando componentes e classes quando adequados. A identidade e os controles específicos da clínica devem continuar claros.

## Risks / Trade-offs

- Mudança da obrigatoriedade de tutor pode abrir acesso indevido → revisar todos os pontos de autorização e testar sessão cruzada e registros legados.
- Corrida entre retirada e adoção → trava transacional comum e testes concorrentes em Xano isolado.
- Clínica pode divulgar incorretamente dados clínicos → manter whitelist existente e confirmação explícita de publicação; não expor dados adicionais.
- Conta de teste fraca → restringir a ambiente isolado, nunca usar em produção e remover após testes.

## Migration Plan

1. Preparar ambiente Xano de desenvolvimento isolado e dados sintéticos; capturar estado anterior e validar compatibilidade da migração.
2. Adicionar identidade, responsabilidade e auditoria; manter pets existentes vinculados a seus tutores e implantar endpoints compatíveis antes da interface.
3. Verificar fluxos clínicos existentes, acesso cruzado, adoção e concorrência; somente então planejar publicação.
4. Em rollback, desativar novos acessos e operações. Preservar pets, transferências e histórico; não restaurar tutor em lote. Pets já criados sob clínica exigem migração autorizada antes de remover a representação de clínica.
