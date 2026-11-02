# Verificação

- Ajuste somente nas regras CSS da agenda veterinária.
- Playwright/Chromium: centro do cabeçalho e da semana coincidem (desvio 0 px)
  nas larguras 1440, 1280, 1180, 1024, 768 e 390 px; nenhuma sobreposição
  entre cabeçalho e controles nem rolagem horizontal.
- Evidências: `evidence/alignment.json` e capturas desktop/celular.
- Aplicação e prévia recompiladas em produção local nas portas 3000 e 3015.
- Verificação repetida com o CSS servido, sem injeção de estilos.
- OpenSpec estrito e `git diff --check`: passaram.
