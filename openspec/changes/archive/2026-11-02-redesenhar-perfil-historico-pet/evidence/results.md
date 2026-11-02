# Verificação

- `reflex compile --dry` passou; build de produção da prévia isolada passou.
- 33 testes de histórico/estado/projeções/agenda passaram. Foto da resposta tem prioridade, fallback exige pet correspondente e autorização da sessão, URI inválida é descartada e falha de autorização limpa o retrato. Testes existentes cobrem resposta antiga, limpeza de sessão e preservação do rascunho.
- Chromium com `history_profile_preview.py` sintético: foto carregada e patinha oculta, patinha com foto ausente/quebrada, cinco contagens consistentes, categorias preservadas, temas claro/escuro, mobile 390px sem overflow, histórico vazio com contagens zero, falha/nova tentativa, Escape, restauração de foco e rascunho preservado. Sem erros JavaScript.
- Capturas `light.png`, `dark.png`, `mobile.png`. A imagem de teste usa um asset sintético local, não foto de paciente real.
- Mascote do cabeçalho ajustado no celular para não sobrepor texto. Botão Voltar e foco seguem a paleta do histórico. Prévia reconstruída e navegador repetido após ajuste final.
- Nenhuma leitura de prontuário real ou publicação remota. `xano/function/clinical/assert_access.xs` foi preparado com campo aditivo foto, após validação de consentimento; ainda requer publicação para fotos no acesso direto sem cache autorizado da agenda.
- `openspec validate redesenhar-perfil-historico-pet --strict` e `git diff --check` passaram.
