# Verificação

- `reflex compile --dry`: passou; build de produção concluído e instância reiniciada em http://localhost:3000.
- `openspec validate corrigir-contraste-tema-claro --strict`: passou.
- `git diff --check`: passou.
- Chromium: login e cadastro claros com preferência Reflex escura preexistente; nenhuma raiz Radix escura permaneceu.
- Componentes representativos de conteúdo clínico, campos, tabela, menu, diálogo e configurações: cores computadas conferidas; contêiner dinâmico corrigido automaticamente; alternância claro → escuro → claro passou; sem erros JavaScript.
- Contraste dos tokens: texto 14,93:1; secundário 6,95:1; placeholder 6,08:1; texto branco sobre botão/sidebar 5,05:1; link 7,07:1. Todos acima de 4,5:1.
- Capturas em `evidence/`; script reproduzível em `tests/integration/run_theme_contrast_browser.py` (requer Playwright e `--chromium CAMINHO`; `--url` e `--output` opcionais).
- Limite: áreas autenticadas verificadas por seus componentes compartilhados representativos, sem login real ou navegação por dados clínicos. As cores globais atendem ambas as áreas; não se afirma auditoria automática de cada combinação dinâmica de conteúdo.
