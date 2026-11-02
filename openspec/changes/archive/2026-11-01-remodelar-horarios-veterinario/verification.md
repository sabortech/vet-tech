# Verificação — Horários do veterinário

## Resultado

Implementação local da agenda visual concluída: menu compartilhado restrito a
Horários/Consultas, identidade e saída; semana de sete dias, calendário nativo,
Hoje, navegação diária, resumo honesto, cards com foto/fallback, status e ações
clínicas existentes. Nenhuma consulta real, conta ou dado clínico foi criado.

## Verificações executadas

- `reflex compile --dry`: todas as páginas compiladas.
- Build de produção pelo launcher: passou; aplicação atualizada em
  `http://localhost:3000/`, frontend e backend na mesma porta.
- 45 testes passaram: `test_veterinary_schedule`, `test_clinical_state`,
  `test_clinical_projections`, `test_unified_navigation`,
  `test_navigation_state` e `test_profile_access`.
- Parser oficial `@xano/xanoscript-language-server`: zero erros no endpoint
  `xano/api/clinical/agenda_GET.xs`. A projeção JavaScript foi executada em Node
  com consentimento ativo/revogado, ordenação, paginação e datas de São Paulo.
- Playwright/Chromium sobre componentes reais em aplicação isolada com dados
  sintéticos na porta 3015: cards por hora, foto, fallback, status, revogação,
  seção Consultas, calendário, estados vazio/erro, paginação, menu recolhido,
  drawer e Escape, telas 1440×1000 e 390×844, tema claro/escuro e menu do tutor.
  Nenhuma exceção JavaScript. Evidências em `evidence/`.
- `git diff --check` e validação estrita da change: passaram.

## Reprodução da revisão visual

`tests/integration/veterinary_schedule_preview.py` é uma aplicação de teste
isolada, com transporte Xano substituído por dados sintéticos; nunca importar
esse módulo no app real. Copiar como `preview/preview.py` num projeto Reflex
em `/tmp` configurado com `app_name="preview"`, definir
`VET_TECH_SOURCE_ROOT` como a raiz do repositório e usar seus assets.
Iniciar em produção com `reflex run --env prod --single-port --backend-port 3015`.
Executar `tests/integration/veterinary_schedule_browser.py --url
http://localhost:3015 --chromium <executável> --output <diretório>` no ambiente
que tem Playwright. A prévia utiliza fotografia pública ilustrativa e dados
fictícios; nenhuma credencial real é necessária.

## Limite de publicação e integração real

A mudança do endpoint é aditiva e está preparada no XanoScript autoritativo.
A tentativa `xano workspace push -d xano -i api/clinical/agenda_GET.xs --dry-run`
selecionou somente esse arquivo, mas retornou `Push preview not yet available on
this instance` e exigiu `--force` no ambiente não interativo. Não foi usado
`--force`, e o endpoint remoto não foi publicado nem sua autorização em banco
retestada com contas reais. O parser e os testes da projeção não substituem esse
teste remoto. Até a publicação do campo `pet_foto`, cards usam o fallback neutro;
as fotos já existentes no cadastro permanecem intactas. O frontend aceita a
resposta antiga sem erro. Não houve migração de tabelas ou alteração de tokens.

Início/retomada e histórico continuam usando os manipuladores existentes; as
permissões e auditoria do backend não foram substituídas pelo menu visual.
Não foi finalizado nenhum atendimento real nesta verificação.
