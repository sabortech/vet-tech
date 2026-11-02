# Verificação

- CSS compartilhado aplicado a links e botões de navegação, conforme o destaque claro exigido em `application-navigation`.
- Navegador Chromium com contas sintéticas de médico e tutor: navegação por Horários, Consultas, Meus Pets, Prontuário, Vacinas e Configurações, conforme disponibilidade de cada perfil.
- Asserções de estilo computado: fundo branco no item ativo, texto e ícone verde-escuros; hover e foco mantêm legibilidade com fundo verde-claro.
- Conferidos temas escuro e claro e abertura do menu móvel em 390 × 844. Sem erros JavaScript.
- Evidências em `evidence/`; roteiro reproduzível em `tests/integration/sidebar_active_theme_browser.py`. O teste aguarda o término das transições CSS antes de comparar cores.
- Aplicação recompilada e recarregada em localhost:3000. Nenhum dado de usuário alterado.
- `openspec validate corrigir-item-ativo-menu-escuro --strict` e `git diff --check` aprovados.

Sem delta de especificação: correção da implementação do contrato existente.
