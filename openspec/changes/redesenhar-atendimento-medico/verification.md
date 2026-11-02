# Verificação

- Framework identificado: Reflex/Python; CSS compartilhado em assets/vet_tech.css, componentes Lucide/Radix, fonte Nunito e mascote global.
- `reflex compile --dry`: sucesso. `openspec validate redesenhar-atendimento-medico --strict`: sucesso. `git diff --check`: sucesso.
- Build e execução em produção da prévia isolada em /tmp/vet-attendance-preview, porta 3018. O servidor real já ocupa a porta 3000 em desenvolvimento; foi preservado.
- Chromium: 1920x1080 e 390x844, sem overflow horizontal ou exceções JavaScript. Evidências em evidence/.
- Conferidos visualmente o vidro, wallpaper fixo durante a rolagem, responsividade, catálogo e resumo do paciente. Conferidos edição, adicionar/remover nos quatro grupos, contadores, confirmação de saída, tema escuro, foco e movimento reduzido.
- Comparação AST dos atributos on_click/on_change/disabled/loading/open: mesmas referências e argumentos antes/depois. Estado, APIs, rotas e backend não foram editados.
- Dados e identidade sintéticos. Não foram acionadas gravações ou finalizações reais no Xano. Histórico e salvamento conservam seus handlers; não foram testados com prontuário real.
- Foto e idade: o resumo disponível não fornece foto; usado placeholder. Nascimento preservado sem acrescentar cálculo de idade ou estado. Feedback utiliza as mensagens existentes, sem inventar horário de salvamento.
- Último acabamento: cor do chevron harmonizada com o texto após a inspeção visual.

## Reproduzir

Copiar tests/integration/attendance_preview.py para preview/preview.py num projeto Reflex temporário configurado com app_name="preview", os mesmos plugins do rxconfig.py e assets apontando para os assets deste projeto. Definir VET_TECH_SOURCE_ROOT para a raiz do VetTech. Não importar a prévia no aplicativo real.

Executar `reflex run --env prod --single-port --backend-port 3018` no projeto temporário. Com Playwright instalado no ambiente de verificação, executar:

```bash
python tests/integration/attendance_browser.py --url http://localhost:3018 --chromium /caminho/para/chrome --output openspec/changes/redesenhar-atendimento-medico/evidence
```
