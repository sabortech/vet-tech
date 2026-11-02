# Design

## Context

A interface já possui abas, busca, filtro de estado, cards e resumo em `veterinary_schedule.py`. `ClinicalMixin.load_agenda` envia `aba/busca/estado`, mas o endpoint publicado consultado via perfil CLI `vettech`, workspace 167758, só declara `dia/page`. A fonte local possui filtros ainda não publicados e Próximas sem limite superior, excluindo hoje. A lista usa `upcoming_rows` em foreach sem divisórias. Ver proposal.md para motivação e decisões do usuário.

## Goals / Non-Goals

**Goals:** tornar os filtros reais e a lista legível por dia, mantendo uma só consulta paginada e os cards existentes.

**Non-Goals:** mudar Horários, criar cancelamento, alterar reservas/prontuários existentes, migrar tabelas ou modificar artefatos da change anterior.

## Decisions

- Filtrar no Xano antes de aplicar 25 itens por página; filtragem somente no frontend daria totais e páginas incorretos. Reutilizar o endpoint e parâmetros existentes, mantendo o modo `dia` da agenda independente das abas.
- Calcular datas civis em America/Sao_Paulo, com janela inclusiva [hoje, hoje + 4 dias] apenas em Próximas. Evitar depender de formatação por locale para aritmética; testar viradas de mês/ano e meia-noite. Não usar a data clínica nem o dia da finalização como chave de agrupamento.
- Publicar contrato identificável, com versão nova para a semântica de cinco dias; o frontend deve exigir esse contrato para Próximas, além das garantias já exigidas para filtros. Não aceitar silenciosamente versão antiga de Próximas.
- Derivar grupos de `upcoming_rows` em computed var com tipos compatíveis com Reflex. Cada grupo terá chave ISO, rótulo e lista de cards, reutilizando seleção, histórico, foto e ações. Preservar ordenação ascendente existente e repetir a divisória ao continuar um dia em outra página. Não criar grupos vazios.
- Reutilizar utilitários de datas e tokens de tema. Rótulos Hoje/Amanhã também em Próximas; os demais dias usam somente DD/MM/AAAA. O intervalo inclui cinco dias civis, não cinco resultados nem cinco dias que tenham consultas.
- Manter busca somente por nomes autorizados, isolamento por veterinário, foto null e auditoria do histórico. Não consultar dados clínicos adicionais para agrupar a lista.
- Conferir novamente o contrato remoto antes da publicação, preparar pacote só do endpoint, executar dry-run e reler a versão publicada. Preservar alterações concorrentes e as fotos já publicadas. Não incluir tabelas, registros ou outros endpoints no pacote.

### População para conferência manual

- Ao implementar, localizar o pet existente Jessy no workspace autenticado e confirmar identidade, tutor e médico com consentimento ativo. Usar o mesmo pet nas cinco consultas. Se houver pets homônimos ou mais de um médico plausível, pedir a referência correta antes de escrever; se faltar consentimento, não criar nem reativar autorização automaticamente.
- Fixar D como o dia civil em America/Sao_Paulo no início da população. Criar exatamente uma consulta agendada em cada data D, D+1, D+2, D+3 e D+4, com horários livres para pet e médico, dentro da faixa usual 08h–17h. Conferir conflitos antes de cada inclusão; não mover nem substituir reservas existentes.
- Hoje pode já ter passado do horário permitido para uma nova reserva pública. Nesse caso, usar inserção administrativa pontual via sessão autenticada da CLI para esses registros de teste explicitamente solicitados, sem flexibilizar a validação da API de agendamento nem alterar seu código. Não inventar atendimento realizado, diagnóstico, vacina, medicamento, doença, exame ou publicação clínica: são apenas reservas com status agendada e motivo claramente identificado como TESTE FILTROS — Jessy.
- Executar a população separadamente do push de código/schema. O pacote de publicação continua contendo somente o endpoint; nunca incluir registros no workspace push.
- Registrar IDs, pet/médico, datas e horários em manifesto privado ignorado pelo Git. Usar identificação estável desta execução e conferir o manifesto e os registros remotos antes de repetir, para não duplicar consultas. Reutilizar apenas reservas criadas por esta população, sem contabilizar consultas reais anteriores como parte das cinco.
- Deixar essas cinco consultas no banco para o usuário conferir e apagar depois, conforme solicitado. A limpeza dos testes automatizados não pode removê-las. Informar no resultado as cinco datas e horários efetivamente criados, e fornecer os IDs ao usuário sem publicar credenciais ou dados pessoais em documentação versionada. Se o processo cruzar a meia-noite, preservar as datas fixadas e explicitar a diferença para o filtro que avança diariamente.
- Atualizar a documentação de verificação com a existência desta população e sua manutenção por solicitação do usuário; manter os detalhes do manifesto no diretório privado.

## Risks / Trade-offs

- Divergência entre fonte local e contrato publicado → confrontar diff e publicar somente o endpoint correspondente ao escopo; registrar evidências.
- Fuso e datas de fronteira → testes determinísticos com relógio controlado; cálculo civil e casos no fim de ano.
- Registros além da página atual → preservar total e paginação, sem prometer que uma única página contém todas as consultas dos cinco dias.
- Mudança de filtro com resposta antiga → manter guards de geração/sessão e limpeza de seleção existentes, cobrindo regressão.
- Duas changes na mesma capacidade → usar requisitos complementares, preservar conteúdo principal e não alterar o planejamento de `redesenhar-consultas-medico`.

- Jessy homônima, consentimento ausente ou horário já reservado → confirmar o vínculo antes de escrever, não ampliar permissões e escolher somente horários livres.
- Reexecução e limpeza automática → manifesto estável e separação entre população mantida e fixtures descartáveis.

## Migration Plan

Sem migração de dados. Implementar e testar fonte e interface; publicar endpoint aditivo com contrato novo; verificar no Xano com dados sintéticos; compilar e reiniciar o frontend usando a mesma versão Reflex do processo existente. Não inicializar uma versão diferente sobre `.web` em uso. Após os filtros publicados e o frontend atualizado, criar e conferir a população manual de cinco consultas da Jessy, mantendo os registros para o usuário. Se backend antigo permanecer, a UI mostra incompatibilidade. Reversão restaura apenas código e mantém os registros.
